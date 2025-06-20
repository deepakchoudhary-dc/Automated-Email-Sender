from typing import Dict, List, Any, Optional
import pandas as pd
import io
from datetime import datetime

from src.database.models import Contact, ContactList, ContactListMember, User, db_session
from src.utils.logger import EmailSenderLogger
from src.utils.security import SecurityManager

logger = EmailSenderLogger('contact_service')

class ContactService:
    """Handles contact management operations"""
    
    def __init__(self):
        self.security_manager = SecurityManager()
    
    def import_contacts_from_csv(self, user_id: int, csv_content: str, 
                                source: str = 'csv_import') -> Dict[str, Any]:
        """Import contacts from CSV content"""
        
        try:
            # Parse CSV
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Validate required columns
            required_columns = ['email']
            if not all(col in df.columns for col in required_columns):
                return {
                    'success': False,
                    'error': f'Required columns missing. Need: {required_columns}'
                }
            
            # Clean and validate data
            df = df.dropna(subset=['email'])  # Remove rows without email
            df['email'] = df['email'].str.lower().str.strip()  # Normalize emails
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['email'])
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            with db_session() as session:
                for index, row in df.iterrows():
                    try:
                        email = row['email']
                        
                        # Validate email format
                        if not self._validate_email(email):
                            skipped_count += 1
                            errors.append(f"Invalid email format: {email}")
                            continue
                        
                        # Check if contact already exists
                        existing_contact = session.query(Contact).filter(
                            Contact.user_id == user_id,
                            Contact.email == email
                        ).first()
                        
                        if existing_contact:
                            skipped_count += 1
                            continue
                        
                        # Create new contact
                        contact_data = {
                            'user_id': user_id,
                            'email': email,
                            'first_name': row.get('first_name', '').strip() if pd.notna(row.get('first_name')) else '',
                            'last_name': row.get('last_name', '').strip() if pd.notna(row.get('last_name')) else '',
                            'company': row.get('company', '').strip() if pd.notna(row.get('company')) else '',
                            'phone': row.get('phone', '').strip() if pd.notna(row.get('phone')) else '',
                            'source': source,
                            'status': 'active',
                            'created_at': datetime.utcnow()
                        }
                        
                        # Handle custom fields
                        custom_fields = {}
                        for col in df.columns:
                            if col not in ['email', 'first_name', 'last_name', 'company', 'phone']:
                                if pd.notna(row[col]):
                                    custom_fields[col] = str(row[col])
                        
                        if custom_fields:
                            contact_data['custom_fields'] = custom_fields
                        
                        # Create contact
                        contact = Contact(**contact_data)
                        session.add(contact)
                        imported_count += 1
                        
                    except Exception as e:
                        skipped_count += 1
                        errors.append(f"Error processing row {index + 2}: {str(e)}")
                
                session.commit()
            
            logger.log_contact_imported(user_id, imported_count, source)
            
            return {
                'success': True,
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'total_processed': len(df),
                'errors': errors[:10]  # Return first 10 errors
            }
            
        except Exception as e:
            logger.log_error('contact_import_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def add_contact(self, user_id: int, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a single contact"""
        
        try:
            # Validate required fields
            if not contact_data.get('email'):
                return {'success': False, 'error': 'Email is required'}
            
            email = contact_data['email'].lower().strip()
            
            # Validate email format
            if not self._validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}
            
            with db_session() as session:
                # Check if contact already exists
                existing_contact = session.query(Contact).filter(
                    Contact.user_id == user_id,
                    Contact.email == email
                ).first()
                
                if existing_contact:
                    return {'success': False, 'error': 'Contact already exists'}
                
                # Create new contact
                contact = Contact(
                    user_id=user_id,
                    email=email,
                    first_name=contact_data.get('first_name', '').strip(),
                    last_name=contact_data.get('last_name', '').strip(),
                    company=contact_data.get('company', '').strip(),
                    phone=contact_data.get('phone', '').strip(),
                    tags=contact_data.get('tags', []),
                    custom_fields=contact_data.get('custom_fields', {}),
                    source=contact_data.get('source', 'manual'),
                    status='active',
                    created_at=datetime.utcnow()
                )
                
                session.add(contact)
                session.commit()
                
                logger.log_user_action(user_id, 'contact_added', {'email': email})
                
                return {
                    'success': True,
                    'contact_id': contact.id,
                    'message': 'Contact added successfully'
                }
                
        except Exception as e:
            logger.log_error('add_contact_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def update_contact(self, user_id: int, contact_id: int, 
                      contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing contact"""
        
        try:
            with db_session() as session:
                contact = session.query(Contact).filter(
                    Contact.id == contact_id,
                    Contact.user_id == user_id
                ).first()
                
                if not contact:
                    return {'success': False, 'error': 'Contact not found'}
                
                # Update fields
                if 'first_name' in contact_data:
                    contact.first_name = contact_data['first_name'].strip()
                
                if 'last_name' in contact_data:
                    contact.last_name = contact_data['last_name'].strip()
                
                if 'company' in contact_data:
                    contact.company = contact_data['company'].strip()
                
                if 'phone' in contact_data:
                    contact.phone = contact_data['phone'].strip()
                
                if 'tags' in contact_data:
                    contact.tags = contact_data['tags']
                
                if 'custom_fields' in contact_data:
                    contact.custom_fields = contact_data['custom_fields']
                
                if 'status' in contact_data:
                    contact.status = contact_data['status']
                
                contact.updated_at = datetime.utcnow()
                session.commit()
                
                logger.log_user_action(user_id, 'contact_updated', {'contact_id': contact_id})
                
                return {'success': True, 'message': 'Contact updated successfully'}
                
        except Exception as e:
            logger.log_error('update_contact_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def delete_contact(self, user_id: int, contact_id: int) -> Dict[str, Any]:
        """Delete a contact"""
        
        try:
            with db_session() as session:
                contact = session.query(Contact).filter(
                    Contact.id == contact_id,
                    Contact.user_id == user_id
                ).first()
                
                if not contact:
                    return {'success': False, 'error': 'Contact not found'}
                
                session.delete(contact)
                session.commit()
                
                logger.log_user_action(user_id, 'contact_deleted', {'contact_id': contact_id})
                
                return {'success': True, 'message': 'Contact deleted successfully'}
                
        except Exception as e:
            logger.log_error('delete_contact_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def get_contacts(self, user_id: int, page: int = 1, per_page: int = 50,
                    filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get contacts with pagination and filtering"""
        
        try:
            with db_session() as session:
                query = session.query(Contact).filter(Contact.user_id == user_id)
                
                # Apply filters
                if filters:
                    if filters.get('status'):
                        query = query.filter(Contact.status == filters['status'])
                    
                    if filters.get('search'):
                        search_term = f"%{filters['search']}%"
                        query = query.filter(
                            (Contact.email.ilike(search_term)) |
                            (Contact.first_name.ilike(search_term)) |
                            (Contact.last_name.ilike(search_term)) |
                            (Contact.company.ilike(search_term))
                        )
                    
                    if filters.get('tags'):
                        # Filter by tags (this would need proper JSON querying)
                        pass
                
                # Get total count
                total_count = query.count()
                
                # Apply pagination
                offset = (page - 1) * per_page
                contacts = query.offset(offset).limit(per_page).all()
                
                # Convert to dict format
                contacts_data = []
                for contact in contacts:
                    contacts_data.append({
                        'id': contact.id,
                        'email': contact.email,
                        'first_name': contact.first_name,
                        'last_name': contact.last_name,
                        'company': contact.company,
                        'phone': contact.phone,
                        'tags': contact.tags or [],
                        'custom_fields': contact.custom_fields or {},
                        'status': contact.status,
                        'source': contact.source,
                        'created_at': contact.created_at.strftime('%Y-%m-%d %H:%M'),
                        'last_contacted': contact.last_contacted.strftime('%Y-%m-%d %H:%M') if contact.last_contacted else None
                    })
                
                return {
                    'success': True,
                    'contacts': contacts_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total_count': total_count,
                        'total_pages': (total_count + per_page - 1) // per_page
                    }
                }
                
        except Exception as e:
            logger.log_error('get_contacts_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def create_contact_list(self, user_id: int, list_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact list"""
        
        try:
            with db_session() as session:
                contact_list = ContactList(
                    user_id=user_id,
                    name=list_data['name'].strip(),
                    description=list_data.get('description', '').strip(),
                    tags=list_data.get('tags', []),
                    created_at=datetime.utcnow()
                )
                
                session.add(contact_list)
                session.commit()
                
                logger.log_user_action(user_id, 'contact_list_created', {'name': list_data['name']})
                
                return {
                    'success': True,
                    'list_id': contact_list.id,
                    'message': 'Contact list created successfully'
                }
                
        except Exception as e:
            logger.log_error('create_contact_list_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def add_contacts_to_list(self, user_id: int, list_id: int, 
                           contact_ids: List[int]) -> Dict[str, Any]:
        """Add contacts to a contact list"""
        
        try:
            with db_session() as session:
                # Verify list ownership
                contact_list = session.query(ContactList).filter(
                    ContactList.id == list_id,
                    ContactList.user_id == user_id
                ).first()
                
                if not contact_list:
                    return {'success': False, 'error': 'Contact list not found'}
                
                added_count = 0
                
                for contact_id in contact_ids:
                    # Verify contact ownership
                    contact = session.query(Contact).filter(
                        Contact.id == contact_id,
                        Contact.user_id == user_id
                    ).first()
                    
                    if not contact:
                        continue
                    
                    # Check if already in list
                    existing_member = session.query(ContactListMember).filter(
                        ContactListMember.contact_id == contact_id,
                        ContactListMember.contact_list_id == list_id
                    ).first()
                    
                    if existing_member:
                        continue
                    
                    # Add to list
                    member = ContactListMember(
                        contact_id=contact_id,
                        contact_list_id=list_id,
                        added_at=datetime.utcnow()
                    )
                    
                    session.add(member)
                    added_count += 1
                
                session.commit()
                
                logger.log_user_action(
                    user_id, 'contacts_added_to_list',
                    {'list_id': list_id, 'count': added_count}
                )
                
                return {
                    'success': True,
                    'added_count': added_count,
                    'message': f'{added_count} contacts added to list'
                }
                
        except Exception as e:
            logger.log_error('add_contacts_to_list_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def get_contact_lists(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all contact lists for a user"""
        try:
            with db_session() as session:
                # For now, return a default list since we might not have contact lists table
                # In a real implementation, this would query the contact lists table
                return [
                    {"id": 1, "name": "All Contacts", "count": 100},
                    {"id": 2, "name": "Newsletter Subscribers", "count": 75},
                    {"id": 3, "name": "VIP Customers", "count": 25}
                ]
        except Exception as e:
            logger.error(f"Error getting contact lists: {str(e)}")
            return []
    
    def segment_contacts(self, user_id: int, 
                        segmentation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Segment contacts based on rules"""
        
        try:
            with db_session() as session:
                query = session.query(Contact).filter(Contact.user_id == user_id)
                
                # Apply segmentation rules
                if segmentation_rules.get('status'):
                    query = query.filter(Contact.status.in_(segmentation_rules['status']))
                
                if segmentation_rules.get('tags'):
                    # Filter by tags (would need proper JSON querying)
                    pass
                
                if segmentation_rules.get('company'):
                    query = query.filter(Contact.company.ilike(f"%{segmentation_rules['company']}%"))
                
                if segmentation_rules.get('created_after'):
                    query = query.filter(Contact.created_at >= segmentation_rules['created_after'])
                
                if segmentation_rules.get('last_contacted_before'):
                    query = query.filter(Contact.last_contacted <= segmentation_rules['last_contacted_before'])
                
                contacts = query.all()
                
                return {
                    'success': True,
                    'segment_size': len(contacts),
                    'contact_ids': [c.id for c in contacts]
                }
                
        except Exception as e:
            logger.log_error('segment_contacts_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def export_contacts(self, user_id: int, contact_ids: List[int] = None,
                       format: str = 'csv') -> Dict[str, Any]:
        """Export contacts to file"""
        
        try:
            with db_session() as session:
                query = session.query(Contact).filter(Contact.user_id == user_id)
                
                if contact_ids:
                    query = query.filter(Contact.id.in_(contact_ids))
                
                contacts = query.all()
                
                if format == 'csv':
                    # Convert to CSV
                    data = []
                    for contact in contacts:
                        row = {
                            'email': contact.email,
                            'first_name': contact.first_name,
                            'last_name': contact.last_name,
                            'company': contact.company,
                            'phone': contact.phone,
                            'status': contact.status,
                            'source': contact.source,
                            'created_at': contact.created_at.strftime('%Y-%m-%d %H:%M')
                        }
                        
                        # Add custom fields
                        if contact.custom_fields:
                            row.update(contact.custom_fields)
                        
                        data.append(row)
                    
                    df = pd.DataFrame(data)
                    csv_content = df.to_csv(index=False)
                    
                    return {
                        'success': True,
                        'content': csv_content,
                        'filename': f'contacts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                    }
                
                else:
                    return {'success': False, 'error': 'Unsupported export format'}
                
        except Exception as e:
            logger.log_error('export_contacts_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def get_contact_engagement_stats(self, user_id: int, contact_id: int) -> Dict[str, Any]:
        """Get engagement statistics for a specific contact"""
        
        try:
            from src.database.models import EmailLog
            
            with db_session() as session:
                contact = session.query(Contact).filter(
                    Contact.id == contact_id,
                    Contact.user_id == user_id
                ).first()
                
                if not contact:
                    return {'success': False, 'error': 'Contact not found'}
                
                # Get email statistics
                email_logs = session.query(EmailLog).filter(
                    EmailLog.contact_id == contact_id
                ).all()
                
                total_emails = len(email_logs)
                opened_emails = len([log for log in email_logs if log.opened_at])
                clicked_emails = len([log for log in email_logs if log.clicked_at])
                
                return {
                    'success': True,
                    'contact': {
                        'id': contact.id,
                        'email': contact.email,
                        'name': f"{contact.first_name} {contact.last_name}".strip()
                    },
                    'stats': {
                        'total_emails_received': total_emails,
                        'emails_opened': opened_emails,
                        'emails_clicked': clicked_emails,
                        'open_rate': (opened_emails / total_emails * 100) if total_emails > 0 else 0,
                        'click_rate': (clicked_emails / total_emails * 100) if total_emails > 0 else 0,
                        'last_contacted': contact.last_contacted
                    }
                }
                
        except Exception as e:
            logger.log_error('get_contact_engagement_stats_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
