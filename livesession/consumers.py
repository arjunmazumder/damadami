import json
import uuid
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from user.models import User
from tag.models import AdminTag, VendorTag
from .models import CallSession
from .utils import generate_agora_token

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Authenticate via JWT token in query string
        query_string = self.scope['query_string'].decode()
        token = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break

        self.user = await self.get_user_from_token(token)
        if self.user is None:
            await self.close()
            return

        await self.accept()

        self.is_vendor = await self.check_if_vendor(self.user)
        
        if self.is_vendor:
            self.group_name = f"vendor_{self.user.id}"
            await self.set_online_status(True)
        else:
            self.group_name = f"buyer_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        if hasattr(self, 'user') and self.user:
            if getattr(self, 'is_vendor', False):
                await self.set_online_status(False)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'initiate_call':
                if self.is_vendor:
                    await self.send(json.dumps({'error': 'Vendors cannot initiate calls.'}))
                    return
                tag_id = data.get('tag_id')
                await self.handle_initiate_call(tag_id)

            elif action == 'accept_call':
                if not self.is_vendor:
                    await self.send(json.dumps({'error': 'Only vendors can accept calls.'}))
                    return
                session_id = data.get('session_id')
                await self.handle_accept_call(session_id)
            elif action == 'cancel_call':
                if self.is_vendor:
                    await self.send(json.dumps({'error': 'Vendors cannot cancel buyer calls. They can only decline.'}))
                    return
                session_id = data.get('session_id')
                await self.handle_cancel_call(session_id)

            elif action == 'decline_call':
                if not self.is_vendor:
                    await self.send(json.dumps({'error': 'Only vendors can decline calls.'}))
                    return
                session_id = data.get('session_id')
                await self.handle_decline_call(session_id)

            elif action == 'reject_call':
                if self.is_vendor:
                    await self.send(json.dumps({'error': 'Vendors cannot reject calls.'}))
                    return
                session_id = data.get('session_id')
                await self.handle_reject_call(session_id)

        except Exception as e:
            await self.send(json.dumps({'error': str(e)}))

    # --- Group Message Handlers ---

    async def incoming_call(self, event):
        await self.send(text_data=json.dumps({
            'type': 'incoming_call',
            'session_id': event['session_id'],
            'tag_name': event['tag_name'],
            'buyer_name': event['buyer_name']
        }))

    async def call_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_started',
            'session_id': event['session_id'],
            'token': event['token'],
            'channel_name': event['channel_name'],
            'uid': event['uid']
        }))

    async def cancel_call(self, event):
        await self.send(text_data=json.dumps({
            'type': 'cancel_call',
            'session_id': event['session_id']
        }))

    async def call_timeout(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_timeout',
            'session_id': event['session_id'],
            'message': event['message']
        }))

    async def call_rejected_by_buyer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_rejected_by_buyer',
            'session_id': event['session_id'],
            'message': 'Buyer has rejected this call.'
        }))

    async def new_invoice(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_invoice',
            'message': 'You have received a new invoice.',
            'invoice': {
                'id': event['invoice_id'],
                'vendor_name': event['vendor_name'],
                'tag_name': event['tag_name'],
                'product_name': event.get('product_name'),
                'short_note_id': event.get('short_note_id'),
                'is_confirm': event.get('is_confirm', False),
                'price_per_piece': event['price_per_piece'],
                'quantity': event['quantity'],
                'total_price': event['total_price'],
                'status': event['status']
            }
        }))

    # --- Business Logic Helpers ---

    async def handle_initiate_call(self, tag_id):
        session, tag_name, online_vendor_ids = await self.create_call_session(self.user.id, tag_id)
        
        if not session:
            await self.send(json.dumps({'error': 'Invalid tag or no online vendors found.'}))
            return

        if not online_vendor_ids:
            await self.send(json.dumps({'error': 'No online vendors for this tag.'}))
            return

        # Broadcast to all matching online vendors
        for v_id in online_vendor_ids:
            await self.channel_layer.group_send(
                f"vendor_{v_id}",
                {
                    'type': 'incoming_call',
                    'session_id': str(session.id),
                    'tag_name': tag_name,
                    'buyer_name': self.user.name or self.user.email
                }
            )
        
        await self.send(json.dumps({
            'type': 'call_searching',
            'session_id': str(session.id),
            'message': 'Searching for vendors...'
        }))
        
        # Start timeout timer in background
        import asyncio
        asyncio.create_task(self.check_timeout(str(session.id), online_vendor_ids))

    async def check_timeout(self, session_id, notified_vendors):
        import asyncio
        await asyncio.sleep(60)
        success = await self.timeout_call_atomic(session_id)
        if success:
            # Notify buyer
            await self.channel_layer.group_send(
                f"buyer_{self.user.id}",
                {
                    'type': 'call_timeout',
                    'session_id': session_id,
                    'message': 'No one answered the call.'
                }
            )
            # Cancel ringing for vendors
            for v_id in notified_vendors:
                await self.channel_layer.group_send(
                    f"vendor_{v_id}",
                    {
                        'type': 'cancel_call',
                        'session_id': session_id
                    }
                )

    async def handle_accept_call(self, session_id):
        # Attempt to be the first to accept using transaction.atomic
        success, session, all_notified_vendors = await self.accept_call_atomic(session_id, self.user.id)

        if not success:
            await self.send(json.dumps({
                'type': 'call_missed',
                'session_id': session_id,
                'message': 'Call already accepted by someone else or cancelled.'
            }))
            return

        # Generate Agora tokens
        buyer_uid = 1
        vendor_uid = 2
        
        buyer_token = generate_agora_token(session.channel_name, buyer_uid)
        await self.channel_layer.group_send(
            f"buyer_{session.buyer_id}",
            {
                'type': 'call_started',
                'session_id': str(session.id),
                'token': buyer_token,
                'channel_name': session.channel_name,
                'uid': buyer_uid
            }
        )

        vendor_token = generate_agora_token(session.channel_name, vendor_uid)
        await self.send(json.dumps({
            'type': 'call_started',
            'session_id': str(session.id),
            'token': vendor_token,
            'channel_name': session.channel_name,
            'uid': vendor_uid
        }))

        # Cancel for other vendors
        for v_id in all_notified_vendors:
            if str(v_id) != str(self.user.id):
                await self.channel_layer.group_send(
                    f"vendor_{v_id}",
                    {
                        'type': 'cancel_call',
                        'session_id': str(session.id)
                    }
                )

    async def handle_cancel_call(self, session_id):
        success, all_notified_vendors = await self.cancel_call_atomic(session_id, self.user.id)
        if success:
            for v_id in all_notified_vendors:
                await self.channel_layer.group_send(
                    f"vendor_{v_id}",
                    {
                        'type': 'cancel_call',
                        'session_id': session_id
                    }
                )
            await self.send(json.dumps({
                'type': 'call_cancelled',
                'session_id': session_id,
                'message': 'You have cancelled the call.'
            }))
        else:
            await self.send(json.dumps({'error': 'Cannot cancel this call.'}))

    async def handle_decline_call(self, session_id):
        await self.send(json.dumps({
            'type': 'call_declined',
            'session_id': session_id,
            'message': 'You have declined the call.'
        }))

    async def handle_reject_call(self, session_id):
        success, session, rejected_vendor_id, new_vendor_ids, tag_name = await self.reject_call_atomic(session_id, self.user.id)
        if not success:
            await self.send(json.dumps({'error': 'Cannot reject this call or call not in connected state.'}))
            return

        # Notify the rejected vendor
        if rejected_vendor_id:
            await self.channel_layer.group_send(
                f"vendor_{rejected_vendor_id}",
                {
                    'type': 'call_rejected_by_buyer',
                    'session_id': str(session.id)
                }
            )

        if not new_vendor_ids:
            await self.send(json.dumps({
                'type': 'call_timeout',
                'session_id': str(session.id),
                'message': 'No other online vendors found.'
            }))
            # Update session to timeout
            await self.timeout_call_atomic(str(session.id))
            return

        # Broadcast incoming call to other online vendors
        for v_id in new_vendor_ids:
            await self.channel_layer.group_send(
                f"vendor_{v_id}",
                {
                    'type': 'incoming_call',
                    'session_id': str(session.id),
                    'tag_name': tag_name,
                    'buyer_name': self.user.name or self.user.email
                }
            )
        
        await self.send(json.dumps({
            'type': 'call_searching',
            'session_id': str(session.id),
            'message': 'Searching for other vendors...'
        }))
        
        # Start timeout timer again
        import asyncio
        asyncio.create_task(self.check_timeout(str(session.id), new_vendor_ids))

    # --- Database Sync to Async ---

    @database_sync_to_async
    def get_user_from_token(self, token):
        if not token: return None
        try:
            print("Received Token:", token)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print("Decoded Payload:", payload)
            user = User.objects.get(id=payload['user_id'])
            print(f"Connected User -> Name: {user.name}, Email: {user.email}")
            return user
        except Exception as e:
            print("Token Error:", str(e))
            return None

    @database_sync_to_async
    def check_if_vendor(self, user):
        return user.role and user.role.value == 'Vendor'

    @database_sync_to_async
    def set_online_status(self, status):
        self.user.is_online = status
        self.user.save(update_fields=['is_online'])

    @database_sync_to_async
    def create_call_session(self, buyer_id, tag_id):
        try:
            tag = AdminTag.objects.get(id=tag_id)
        except AdminTag.DoesNotExist:
            return None, None, []

        vendor_tags = VendorTag.objects.filter(admin_tag=tag, vendor__is_online=True)
        vendor_ids = list(vendor_tags.values_list('vendor_id', flat=True))

        if not vendor_ids:
            return None, None, []

        channel_name = str(uuid.uuid4())
        session = CallSession.objects.create(
            buyer_id=buyer_id,
            tag=tag,
            channel_name=channel_name,
            status='searching'
        )
        return session, tag.tagname, vendor_ids

    @database_sync_to_async
    def accept_call_atomic(self, session_id, vendor_id):
        with transaction.atomic():
            try:
                session = CallSession.objects.select_for_update().get(id=session_id)
                if session.status != 'searching':
                    return False, None, []
                
                session.status = 'connected'
                session.vendor_id = vendor_id
                session.start_time = timezone.now()
                session.save()

                vendor_tags = VendorTag.objects.filter(admin_tag=session.tag)
                vendor_ids = list(vendor_tags.values_list('vendor_id', flat=True))

                return True, session, vendor_ids
            except CallSession.DoesNotExist:
                return False, None, []

    @database_sync_to_async
    def cancel_call_atomic(self, session_id, buyer_id):
        with transaction.atomic():
            try:
                session = CallSession.objects.select_for_update().get(id=session_id, buyer_id=buyer_id)
                if session.status not in ['searching', 'connected']:
                    return False, []
                
                was_connected = (session.status == 'connected')
                accepted_vendor_id = session.vendor_id if was_connected else None
                
                session.status = 'completed' if was_connected else 'cancelled'
                if was_connected:
                    session.end_time = timezone.now()
                    if session.start_time:
                        session.duration = session.end_time - session.start_time
                session.save()
                
                if was_connected and accepted_vendor_id:
                    return True, [accepted_vendor_id]
                else:
                    vendor_tags = VendorTag.objects.filter(admin_tag=session.tag)
                    vendor_ids = list(vendor_tags.values_list('vendor_id', flat=True))
                    return True, vendor_ids
            except CallSession.DoesNotExist:
                return False, []

    @database_sync_to_async
    def timeout_call_atomic(self, session_id):
        with transaction.atomic():
            try:
                session = CallSession.objects.select_for_update().get(id=session_id)
                if session.status == 'searching':
                    session.status = 'timeout'
                    session.save()
                    return True
                return False
            except CallSession.DoesNotExist:
                return False

    @database_sync_to_async
    def reject_call_atomic(self, session_id, buyer_id):
        with transaction.atomic():
            try:
                session = CallSession.objects.select_for_update().get(id=session_id, buyer_id=buyer_id)
                if session.status != 'connected' or not session.vendor:
                    return False, None, None, [], None
                
                rejected_vendor_id = session.vendor.id
                session.status = 'searching'
                
                session.rejected_vendors.add(session.vendor)
                
                session.vendor = None
                session.save()
                
                # Find other online vendors for this tag
                vendor_tags = VendorTag.objects.filter(admin_tag=session.tag, vendor__is_online=True)
                all_vendor_ids = list(vendor_tags.values_list('vendor_id', flat=True))
                
                # Exclude rejected vendors
                rejected_vendor_ids = list(session.rejected_vendors.values_list('id', flat=True))
                new_vendor_ids = [vid for vid in all_vendor_ids if vid not in rejected_vendor_ids]
                
                return True, session, rejected_vendor_id, new_vendor_ids, session.tag.tagname
            except CallSession.DoesNotExist:
                return False, None, None, [], None
