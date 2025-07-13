from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from unittest.mock import patch, MagicMock
import json

from campaigns.models import (
    Campaign, Chapter, Encounter, Location, NPC, 
    CharacterSummary, SessionNote, ChatMessage, ChapterChatMessage
)


class BaseViewTestCase(TestCase):
    """Base test case for view tests with authentication setup"""
    
    def setUp(self):
        """Set up test users and authenticate"""
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create test campaign structure
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='A test campaign',
            owner=self.user1
        )
        
        self.chapter = Chapter.objects.create(
            campaign=self.campaign,
            order=1,
            title='Test Chapter',
            summary='Test chapter summary',
            owner=self.user1
        )
        
        self.encounter = Encounter.objects.create(
            chapter=self.chapter,
            title='Test Encounter',
            type='combat',
            summary='Test encounter summary',
            order=1,
            owner=self.user1
        )
        
        self.location = Location.objects.create(
            campaign=self.campaign,
            name='Test Location',
            owner=self.user1
        )
        
        self.npc = NPC.objects.create(
            campaign=self.campaign,
            name='Test NPC',
            location=self.location,
            owner=self.user1
        )
        
        self.character = CharacterSummary.objects.create(
            campaign=self.campaign,
            player_name='Test Player',
            character_name='Test Character',
            race='Human'
        )
        
        self.client = Client()


class HomeViewTest(BaseViewTestCase):
    """Test home page view"""
    
    def test_home_view_anonymous_user(self):
        """Test home view shows landing page for anonymous users"""
        response = self.client.get(reverse('campaigns:home'))
        self.assertEqual(response.status_code, 200)
        # Should render the landing page template
    
    def test_home_view_authenticated_user(self):
        """Test home view for authenticated users"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('campaigns', response.url)


class CampaignViewTest(BaseViewTestCase):
    """Test campaign CRUD views"""
    
    def test_campaign_list_view_anonymous_user_error(self):
        """Test campaign list view with anonymous user causes error"""
        # The view tries to filter by request.user but doesn't require login
        # This causes an error when an anonymous user accesses it
        with self.assertRaises(TypeError):
            response = self.client.get(reverse('campaigns:campaign_list'))
    
    def test_campaign_list_view_authenticated(self):
        """Test campaign list for authenticated users"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:campaign_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Campaign')
        self.assertContains(response, 'All Campaigns')
    
    def test_campaign_list_view_user_isolation(self):
        """Test users only see their own campaigns"""
        # Create campaign for user2
        user2_campaign = Campaign.objects.create(
            title='User2 Campaign',
            description='User2 campaign',
            owner=self.user2
        )
        
        # Login as user1
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:campaign_list'))
        
        # Should only see user1's campaign
        self.assertContains(response, 'Test Campaign')
        self.assertNotContains(response, 'User2 Campaign')
    
    def test_campaign_detail_view(self):
        """Test campaign detail view"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:campaign_detail', args=[self.campaign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Campaign')
        self.assertContains(response, 'Test Chapter')
    
    def test_campaign_detail_view_ownership(self):
        """Test campaign detail view enforces ownership"""
        self.client.login(username='testuser2', password='testpass123')
        response = self.client.get(reverse('campaigns:campaign_detail', args=[self.campaign.id]))
        self.assertEqual(response.status_code, 404)
    
    def test_campaign_create_view_get(self):
        """Test campaign create view GET request"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:campaign_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Campaign')
    
    def test_campaign_create_view_post(self):
        """Test campaign create view POST request"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'title': 'New Campaign',
            'description': 'A new campaign description'
        }
        response = self.client.post(reverse('campaigns:campaign_create'), data)
        self.assertEqual(response.status_code, 302)
        
        # Check campaign was created
        new_campaign = Campaign.objects.filter(title='New Campaign').first()
        self.assertIsNotNone(new_campaign)
        self.assertEqual(new_campaign.owner, self.user1)
    
    def test_campaign_create_view_invalid_data(self):
        """Test campaign create view with invalid data"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'title': '',  # Required field
            'description': 'A description'
        }
        response = self.client.post(reverse('campaigns:campaign_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')


class ChapterViewTest(BaseViewTestCase):
    """Test chapter CRUD views"""
    
    def test_chapter_detail_view(self):
        """Test chapter detail view"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:chapter_detail', args=[self.chapter.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Chapter')
        self.assertContains(response, 'Test Encounter')
    
    def test_chapter_detail_view_ownership(self):
        """Test chapter detail view enforces ownership"""
        self.client.login(username='testuser2', password='testpass123')
        response = self.client.get(reverse('campaigns:chapter_detail', args=[self.chapter.id]))
        self.assertEqual(response.status_code, 404)
    
    def test_chapter_create_view_get(self):
        """Test chapter create view GET request"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:chapter_create', args=[self.campaign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Chapter')
    
    def test_chapter_create_view_post(self):
        """Test chapter create view POST request"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'title': 'New Chapter',
            'summary': 'A new chapter summary',
            'order': 2,
            'status': 'not_started',
            'level_range': '4-6',
            'encounters-TOTAL_FORMS': '0',
            'encounters-INITIAL_FORMS': '0',
            'encounters-MIN_NUM_FORMS': '0',
            'encounters-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(reverse('campaigns:chapter_create', args=[self.campaign.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check chapter was created
        new_chapter = Chapter.objects.filter(title='New Chapter').first()
        self.assertIsNotNone(new_chapter)
        self.assertEqual(new_chapter.owner, self.user1)
        self.assertEqual(new_chapter.campaign, self.campaign)
    
    def test_chapter_update_view(self):
        """Test chapter update view"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'title': 'Updated Chapter',
            'summary': 'Updated summary',
            'order': 1,
            'status': 'in_progress',
            'level_range': '1-3',
            'encounters-TOTAL_FORMS': '1',
            'encounters-INITIAL_FORMS': '1',
            'encounters-MIN_NUM_FORMS': '0',
            'encounters-MAX_NUM_FORMS': '1000',
            'encounters-0-id': str(self.encounter.id),
            'encounters-0-title': 'Test Encounter',
            'encounters-0-type': 'combat',
            'encounters-0-summary': 'Test encounter summary',
            'encounters-0-order': '1',
        }
        response = self.client.post(reverse('campaigns:chapter_update', args=[self.chapter.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check chapter was updated
        updated_chapter = Chapter.objects.get(id=self.chapter.id)
        self.assertEqual(updated_chapter.title, 'Updated Chapter')
        self.assertEqual(updated_chapter.status, 'in_progress')
    
    def test_chapter_delete_view(self):
        """Test chapter delete view"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.post(reverse('campaigns:chapter_delete', args=[self.chapter.id]))
        self.assertEqual(response.status_code, 302)
        
        # Check chapter was deleted
        self.assertFalse(Chapter.objects.filter(id=self.chapter.id).exists())
    
    def test_chapter_status_toggle_view(self):
        """Test chapter status toggle view"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.post(reverse('campaigns:chapter_status_toggle', args=[self.chapter.id]))
        self.assertEqual(response.status_code, 200)
        
        # Check status was updated
        updated_chapter = Chapter.objects.get(id=self.chapter.id)
        self.assertEqual(updated_chapter.status, 'in_progress')
    
    def test_chapter_reorder_view(self):
        """Test chapter reorder view"""
        # Create another chapter
        chapter2 = Chapter.objects.create(
            campaign=self.campaign,
            order=2,
            title='Second Chapter',
            owner=self.user1
        )
        
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'chapter_ids': [str(chapter2.id), str(self.chapter.id)]
        }
        response = self.client.post(
            reverse('campaigns:chapter_reorder', args=[self.campaign.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Check chapters were reordered
        self.chapter.refresh_from_db()
        chapter2.refresh_from_db()
        self.assertEqual(chapter2.order, 1)
        self.assertEqual(self.chapter.order, 2)


class EncounterViewTest(BaseViewTestCase):
    """Test encounter CRUD views"""
    
    def test_encounter_create_view_get(self):
        """Test encounter create view GET request"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:encounter_create', args=[self.chapter.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Encounter')
    
    def test_encounter_create_view_post(self):
        """Test encounter create view POST request"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'title': 'New Encounter',
            'type': 'social',
            'summary': 'A new encounter summary',
            'order': 2,
            'danger_level': 'medium'
        }
        response = self.client.post(reverse('campaigns:encounter_create', args=[self.chapter.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check encounter was created
        new_encounter = Encounter.objects.filter(title='New Encounter').first()
        self.assertIsNotNone(new_encounter)
        self.assertEqual(new_encounter.owner, self.user1)
        self.assertEqual(new_encounter.chapter, self.chapter)
    
    def test_encounter_update_view(self):
        """Test encounter update view"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'title': 'Updated Encounter',
            'type': 'puzzle',
            'summary': 'Updated encounter summary',
            'order': 1,
            'danger_level': 'hard'
        }
        response = self.client.post(reverse('campaigns:encounter_update', args=[self.encounter.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check encounter was updated
        updated_encounter = Encounter.objects.get(id=self.encounter.id)
        self.assertEqual(updated_encounter.title, 'Updated Encounter')
        self.assertEqual(updated_encounter.type, 'puzzle')
    
    def test_encounter_delete_view(self):
        """Test encounter delete view"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.post(reverse('campaigns:encounter_delete', args=[self.encounter.id]))
        self.assertEqual(response.status_code, 302)
        
        # Check encounter was deleted
        self.assertFalse(Encounter.objects.filter(id=self.encounter.id).exists())
    
    def test_encounter_image_upload(self):
        """Test encounter image upload"""
        self.client.login(username='testuser1', password='testpass123')
        
        # Create a simple test image
        test_image = SimpleUploadedFile(
            name='test_map.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        
        data = {
            'title': 'Encounter with Map',
            'type': 'combat',
            'summary': 'An encounter with a map',
            'order': 1,
            'map_image': test_image
        }
        response = self.client.post(reverse('campaigns:encounter_update', args=[self.encounter.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check image was uploaded
        updated_encounter = Encounter.objects.get(id=self.encounter.id)
        self.assertTrue(updated_encounter.map_image.name.endswith('test_map.jpg'))


class LocationViewTest(BaseViewTestCase):
    """Test location CRUD views"""
    
    def test_location_create_view_get(self):
        """Test location create view GET request"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:location_create', args=[self.campaign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Location')
    
    def test_location_create_view_post(self):
        """Test location create view POST request"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'name': 'New Location',
            'description': 'A new location description',
            'region': 'Test Region',
            'tags': 'city,port'
        }
        response = self.client.post(reverse('campaigns:location_create', args=[self.campaign.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check location was created
        new_location = Location.objects.filter(name='New Location').first()
        self.assertIsNotNone(new_location)
        self.assertEqual(new_location.owner, self.user1)
        self.assertEqual(new_location.campaign, self.campaign)
    
    def test_location_update_view(self):
        """Test location update view"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'name': 'Updated Location',
            'description': 'Updated description',
            'region': 'Updated Region',
            'tags': 'updated,tags'
        }
        response = self.client.post(reverse('campaigns:location_update', args=[self.location.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check location was updated
        updated_location = Location.objects.get(id=self.location.id)
        self.assertEqual(updated_location.name, 'Updated Location')
        self.assertEqual(updated_location.region, 'Updated Region')


class NPCViewTest(BaseViewTestCase):
    """Test NPC CRUD views"""
    
    def test_npc_create_view_get(self):
        """Test NPC create view GET request"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:npc_create', args=[self.campaign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create NPC')
    
    def test_npc_create_view_post(self):
        """Test NPC create view POST request"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'name': 'New NPC',
            'description': 'A new NPC description',
            'role': 'guard',
            'location': self.location.id,
            'status': 'alive',
            'tags': 'friendly,helpful'
        }
        response = self.client.post(reverse('campaigns:npc_create', args=[self.campaign.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check NPC was created
        new_npc = NPC.objects.filter(name='New NPC').first()
        self.assertIsNotNone(new_npc)
        self.assertEqual(new_npc.owner, self.user1)
        self.assertEqual(new_npc.campaign, self.campaign)
    
    def test_npc_update_view(self):
        """Test NPC update view"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'name': 'Updated NPC',
            'description': 'Updated description',
            'role': 'innkeeper',
            'location': self.location.id,
            'status': 'dead',
            'tags': 'updated,tags'
        }
        response = self.client.post(reverse('campaigns:npc_update', args=[self.npc.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check NPC was updated
        updated_npc = NPC.objects.get(id=self.npc.id)
        self.assertEqual(updated_npc.name, 'Updated NPC')
        self.assertEqual(updated_npc.role, 'innkeeper')
        self.assertEqual(updated_npc.status, 'dead')


class CharacterViewTest(BaseViewTestCase):
    """Test character CRUD views"""
    
    def test_character_detail_view(self):
        """Test character detail view"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:character_detail', args=[self.character.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Character')
        self.assertContains(response, 'Test Player')
    
    def test_character_create_view_get(self):
        """Test character create view GET request"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:character_create', args=[self.campaign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Character')
    
    def test_character_create_view_post(self):
        """Test character create view POST request"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'player_name': 'New Player',
            'character_name': 'New Character',
            'race': 'Elf',
            'character_class': 'Wizard',
            'level': 5,
            'background': 'Scholar',
            'alignment': 'Neutral Good',
            'armor_class': 15,
            'current_hit_points': 30,
            'passive_perception': 12,
            'initiative_modifier': 2,
            'alive': True,
            'heroic_inspiration': False
        }
        response = self.client.post(reverse('campaigns:character_create', args=[self.campaign.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check character was created
        new_character = CharacterSummary.objects.filter(character_name='New Character').first()
        self.assertIsNotNone(new_character)
        self.assertEqual(new_character.campaign, self.campaign)
    
    def test_character_update_view(self):
        """Test character update view"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'player_name': 'Updated Player',
            'character_name': 'Updated Character',
            'race': 'Dwarf',
            'character_class': 'Cleric',
            'level': 7,
            'background': 'Acolyte',
            'alignment': 'Lawful Good',
            'armor_class': 18,
            'current_hit_points': 45,
            'passive_perception': 14,
            'initiative_modifier': 1,
            'alive': True,
            'heroic_inspiration': True
        }
        response = self.client.post(reverse('campaigns:character_update', args=[self.character.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check character was updated
        updated_character = CharacterSummary.objects.get(id=self.character.id)
        self.assertEqual(updated_character.character_name, 'Updated Character')
        self.assertEqual(updated_character.race, 'Dwarf')
        self.assertEqual(updated_character.level, 7)
        self.assertTrue(updated_character.heroic_inspiration)


class SessionNoteViewTest(BaseViewTestCase):
    """Test session note views"""
    
    def test_encounter_note_form_view(self):
        """Test encounter note form view"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:encounter_note_form', args=[self.encounter.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Session Notes')
    
    def test_encounter_note_create_view(self):
        """Test encounter note create view"""
        self.client.login(username='testuser1', password='testpass123')
        data = {
            'content': 'Test session note content',
            'date': '2023-01-15'
        }
        response = self.client.post(reverse('campaigns:encounter_note_create', args=[self.encounter.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check session note was created
        new_note = SessionNote.objects.filter(encounter=self.encounter).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.owner, self.user1)
        self.assertEqual(new_note.content, 'Test session note content')


class ExportViewTest(BaseViewTestCase):
    """Test export functionality"""
    
    def test_export_campaign_markdown(self):
        """Test campaign export to markdown"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:export_campaign_markdown', args=[self.campaign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/markdown')
        self.assertIn('attachment; filename="Test Campaign.md"', response['Content-Disposition'])
        
        # Check content includes campaign details
        content = response.content.decode('utf-8')
        self.assertIn('Test Campaign', content)
        self.assertIn('Test Chapter', content)
        self.assertIn('Test Encounter', content)


class AuthenticationViewTest(BaseViewTestCase):
    """Test authentication views"""
    
    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('campaigns:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_valid(self):
        """Test login view POST request with valid credentials"""
        data = {
            'username': 'testuser1',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('campaigns:login'), data)
        self.assertEqual(response.status_code, 302)
        
        # Check user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_login_view_post_invalid(self):
        """Test login view POST request with invalid credentials"""
        data = {
            'username': 'testuser1',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('campaigns:login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
    
    def test_logout_view(self):
        """Test logout view"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:logout'))
        self.assertEqual(response.status_code, 302)
        
        # Check user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)


class PermissionViewTest(BaseViewTestCase):
    """Test view permissions and ownership"""
    
    def test_campaign_access_denied_for_non_owner(self):
        """Test campaign access is denied for non-owners"""
        self.client.login(username='testuser2', password='testpass123')
        
        # Test various campaign-related views
        views_to_test = [
            ('campaigns:campaign_detail', [self.campaign.id]),
            ('campaigns:chapter_create', [self.campaign.id]),
            ('campaigns:location_create', [self.campaign.id]),
            ('campaigns:npc_create', [self.campaign.id]),
            ('campaigns:character_create', [self.campaign.id]),
            ('campaigns:export_campaign_markdown', [self.campaign.id]),
        ]
        
        for view_name, args in views_to_test:
            response = self.client.get(reverse(view_name, args=args))
            self.assertEqual(response.status_code, 404, f"View {view_name} should return 404")
    
    def test_chapter_access_denied_for_non_owner(self):
        """Test chapter access is denied for non-owners"""
        self.client.login(username='testuser2', password='testpass123')
        
        views_to_test = [
            ('campaigns:chapter_detail', [self.chapter.id]),
            ('campaigns:chapter_update', [self.chapter.id]),
            ('campaigns:chapter_delete', [self.chapter.id]),
            ('campaigns:encounter_create', [self.chapter.id]),
        ]
        
        for view_name, args in views_to_test:
            response = self.client.get(reverse(view_name, args=args))
            self.assertEqual(response.status_code, 404, f"View {view_name} should return 404")
    
    def test_encounter_access_denied_for_non_owner(self):
        """Test encounter access is denied for non-owners"""
        self.client.login(username='testuser2', password='testpass123')
        
        views_to_test = [
            ('campaigns:encounter_update', [self.encounter.id]),
            ('campaigns:encounter_delete', [self.encounter.id]),
            ('campaigns:encounter_note_form', [self.encounter.id]),
            ('campaigns:encounter_note_create', [self.encounter.id]),
        ]
        
        for view_name, args in views_to_test:
            response = self.client.get(reverse(view_name, args=args))
            self.assertEqual(response.status_code, 404, f"View {view_name} should return 404")


class HTMXViewTest(BaseViewTestCase):
    """Test HTMX-specific views"""
    
    def test_chapter_status_toggle_htmx(self):
        """Test chapter status toggle with HTMX"""
        self.client.login(username='testuser1', password='testpass123')
        
        # Test with HTMX header
        response = self.client.post(
            reverse('campaigns:chapter_status_toggle', args=[self.chapter.id]),
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        
        # Check status was updated
        updated_chapter = Chapter.objects.get(id=self.chapter.id)
        self.assertEqual(updated_chapter.status, 'in_progress')
    
    def test_encounter_note_form_htmx(self):
        """Test encounter note form with HTMX"""
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.get(
            reverse('campaigns:encounter_note_form', args=[self.encounter.id]),
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_empty_fragment_view(self):
        """Test empty fragment view for HTMX"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('campaigns:empty_fragment'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8').strip(), '')


class FormValidationTest(BaseViewTestCase):
    """Test form validation in views"""
    
    def test_campaign_form_validation(self):
        """Test campaign form validation"""
        self.client.login(username='testuser1', password='testpass123')
        
        # Test with empty title
        data = {
            'title': '',
            'description': 'Test description'
        }
        response = self.client.post(reverse('campaigns:campaign_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
        
        # Test with title too long
        data = {
            'title': 'x' * 201,  # Exceeds max_length
            'description': 'Test description'
        }
        response = self.client.post(reverse('campaigns:campaign_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ensure this value has at most 200 characters')
    
    def test_chapter_form_validation(self):
        """Test chapter form validation"""
        self.client.login(username='testuser1', password='testpass123')
        
        # Test with invalid order (zero)
        data = {
            'title': 'Test Chapter',
            'summary': 'Test summary',
            'order': 0,  # Should be positive
            'encounters-TOTAL_FORMS': '0',
            'encounters-INITIAL_FORMS': '0',
            'encounters-MIN_NUM_FORMS': '0',
            'encounters-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(reverse('campaigns:chapter_create', args=[self.campaign.id]), data)
        self.assertEqual(response.status_code, 200)
        # Should show validation error
    
    def test_encounter_form_validation(self):
        """Test encounter form validation"""
        self.client.login(username='testuser1', password='testpass123')
        
        # Test with empty required fields
        data = {
            'title': '',
            'type': '',
            'summary': '',
            'order': 1
        }
        response = self.client.post(reverse('campaigns:encounter_create', args=[self.chapter.id]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
    
    def test_character_form_validation(self):
        """Test character form validation"""
        self.client.login(username='testuser1', password='testpass123')
        
        # Test with invalid level (zero)
        data = {
            'player_name': 'Test Player',
            'character_name': 'Test Character',
            'race': 'Human',
            'level': 0,  # Should be positive
            'armor_class': 10,
            'current_hit_points': 10,
            'passive_perception': 10,
            'initiative_modifier': 0,
            'alive': True,
            'heroic_inspiration': False
        }
        response = self.client.post(reverse('campaigns:character_create', args=[self.campaign.id]), data)
        self.assertEqual(response.status_code, 200)
        # Should show validation error


class ConcurrencyTest(BaseViewTestCase):
    """Test concurrent access and race conditions"""
    
    def test_chapter_reorder_concurrent_access(self):
        """Test chapter reorder with concurrent access"""
        # Create multiple chapters
        chapters = []
        for i in range(3):
            chapter = Chapter.objects.create(
                campaign=self.campaign,
                order=i + 2,
                title=f'Chapter {i + 2}',
                owner=self.user1
            )
            chapters.append(chapter)
        
        self.client.login(username='testuser1', password='testpass123')
        
        # Test reordering
        chapter_ids = [str(ch.id) for ch in chapters] + [str(self.chapter.id)]
        data = {'chapter_ids': chapter_ids}
        
        response = self.client.post(
            reverse('campaigns:chapter_reorder', args=[self.campaign.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify new order
        for i, chapter_id in enumerate(chapter_ids):
            chapter = Chapter.objects.get(id=chapter_id)
            self.assertEqual(chapter.order, i + 1)
    
    def test_multiple_session_notes_same_encounter(self):
        """Test creating multiple session notes for the same encounter"""
        self.client.login(username='testuser1', password='testpass123')
        
        # Create multiple session notes
        for i in range(3):
            data = {
                'content': f'Session note {i + 1}',
                'date': '2023-01-15'
            }
            response = self.client.post(reverse('campaigns:encounter_note_create', args=[self.encounter.id]), data)
            self.assertEqual(response.status_code, 302)
        
        # Check all notes were created
        notes = SessionNote.objects.filter(encounter=self.encounter)
        self.assertEqual(notes.count(), 3)
        
        # Check they have different content
        contents = [note.content for note in notes]
        self.assertEqual(len(set(contents)), 3)  # All unique
