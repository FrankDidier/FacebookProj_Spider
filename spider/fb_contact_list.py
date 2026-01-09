# -*- coding: utf-8 -*-
"""
FB Contact List - Generate contact lists
"""
import autoads
from autoads.log import log
from autoads import tools
from autoads.config import config
import random
import string
import os
import csv


class ContactListGenerator:
    """Generate contact lists with various options"""
    
    @staticmethod
    def generate_english_names(count):
        """Generate English contact names"""
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa', 
                      'Robert', 'Mary', 'James', 'Patricia', 'Michael', 'Jennifer', 'William', 'Linda']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas', 'Taylor']
        
        contacts = []
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            contacts.append(f"{first} {last}")
        
        return contacts
    
    @staticmethod
    def generate_phone_numbers(count, country_code='+1', area_code='', sequential=False):
        """Generate phone numbers"""
        if not area_code:
            area_code = str(random.randint(200, 999))
        
        numbers = []
        base_number = random.randint(1000000, 9999999) if not sequential else 1000000
        
        for i in range(count):
            if sequential:
                number = f"{country_code}{area_code}{base_number + i}"
            else:
                number = f"{country_code}{area_code}{random.randint(1000000, 9999999)}"
            numbers.append(number)
        
        return numbers
    
    @staticmethod
    def generate_contacts(count, region='US', language='en', country_code='+1', area_code='', sequential=False):
        """Generate contact list"""
        contacts = []
        
        if language == 'en':
            names = ContactListGenerator.generate_english_names(count)
        else:
            # Add other language support here
            names = ContactListGenerator.generate_english_names(count)
        
        phone_numbers = ContactListGenerator.generate_phone_numbers(count, country_code, area_code, sequential)
        
        for i in range(count):
            contact = {
                'name': names[i],
                'phone': phone_numbers[i],
                'region': region
            }
            contacts.append(contact)
        
        return contacts
    
    @staticmethod
    def save_contacts(contacts, file_path):
        """Save contacts to file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Phone', 'Region'])
                for contact in contacts:
                    writer.writerow([contact['name'], contact['phone'], contact['region']])
            
            return True
        except Exception as e:
            log.error(f"Error saving contacts: {e}")
            return False
    
    @staticmethod
    def import_from_file(file_path):
        """Import contacts from text file"""
        contacts = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Assume format: Name,Phone or just Phone
                        parts = line.split(',')
                        if len(parts) >= 2:
                            contacts.append({'name': parts[0], 'phone': parts[1]})
                        else:
                            contacts.append({'name': '', 'phone': parts[0]})
            
            return contacts
        except Exception as e:
            log.error(f"Error importing contacts: {e}")
            return []


class ContactListSpider(autoads.AirSpider):
    """Generate and manage contact lists"""
    
    def start_requests(self):
        # Get ads_ids for window arrangement
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums) if hasattr(self.config, 'account_nums') else []
        
        contact_action = getattr(config, 'contact_action', 'generate')  # generate, import
        contact_count = getattr(config, 'contact_count', 100)
        contact_region = getattr(config, 'contact_region', 'US')
        contact_language = getattr(config, 'contact_language', 'en')
        contact_country_code = getattr(config, 'contact_country_code', '+1')
        contact_area_code = getattr(config, 'contact_area_code', '')
        contact_sequential = getattr(config, 'contact_sequential', False)
        contact_file_path = getattr(config, 'contact_file_path', './contacts/contact_list.txt')
        contact_import_file = getattr(config, 'contact_import_file', '')
        
        tools.send_message_to_ui(self.ms, self.ui, 
                                 f"开始联系人列表操作: 操作={contact_action}")
        
        if contact_action == 'generate':
            # Generate contacts
            contacts = ContactListGenerator.generate_contacts(
                contact_count,
                contact_region,
                contact_language,
                contact_country_code,
                contact_area_code,
                contact_sequential
            )
            
            if ContactListGenerator.save_contacts(contacts, contact_file_path):
                tools.send_message_to_ui(self.ms, self.ui, 
                                        f"联系人列表生成成功: {len(contacts)} 个联系人")
                tools.send_message_to_ui(self.ms, self.ui, 
                                        f"保存路径: {contact_file_path}")
            else:
                tools.send_message_to_ui(self.ms, self.ui, "联系人列表生成失败")
        
        elif contact_action == 'import':
            # Import contacts from file
            if contact_import_file and os.path.exists(contact_import_file):
                contacts = ContactListGenerator.import_from_file(contact_import_file)
                
                if contacts:
                    # Save imported contacts
                    if ContactListGenerator.save_contacts(contacts, contact_file_path):
                        tools.send_message_to_ui(self.ms, self.ui, 
                                                f"联系人列表导入成功: {len(contacts)} 个联系人")
                    else:
                        tools.send_message_to_ui(self.ms, self.ui, "联系人列表保存失败")
                else:
                    tools.send_message_to_ui(self.ms, self.ui, "联系人列表导入失败")
            else:
                tools.send_message_to_ui(self.ms, self.ui, "导入文件不存在")
        
        # This spider doesn't need browser automation, but yield empty for consistency
        # If needed, can yield a request for browser-based contact sync
        if hasattr(self, 'stop_event') and self.stop_event and self.stop_event.is_set():
            return
        
        # No browser requests needed for contact list generation
        return
        yield  # Make it a generator
    
    def parse(self, request, response):
        """Parse response - ContactListSpider mainly generates locally, this handles any web-based operations"""
        browser = response.browser
        if not browser:
            return
        
        # Check for stop event
        if hasattr(request, 'stop_event') and request.stop_event and request.stop_event.is_set():
            return
        
        # This spider primarily generates contacts locally
        # This parse method is for potential future web-based contact import/export
        pass

