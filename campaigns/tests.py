from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch, MagicMock
import json
from datetime import date, timedelta

from campaigns.models import (
    Campaign, Chapter, Encounter, Location, NPC, 
    CharacterSummary, SessionNote, ChatMessage, ChapterChatMessage
)
from campaigns.services.llm import generate_session_summary


class BaseTestCase(TestCase):
    """Base test case with common setup for all campaign tests"""
    
    def setUp(self):
        """Set up test users and basic campaign structure"""
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
        
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='A test campaign for unit testing',
            owner=self.user1
        )
        
        self.chapter = Chapter.objects.create(
            campaign=self.campaign,
            order=1,
            title='Test Chapter',
            summary='Test chapter summary',
            level_range='1-3',
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
            description='A test location',
            region='Test Region',
            owner=self.user1
        )
        
        self.npc = NPC.objects.create(
            campaign=self.campaign,
            name='Test NPC',
            description='A test NPC',
            role='merchant',
            location=self.location,
            owner=self.user1
        )
        
        self.character = CharacterSummary.objects.create(
            campaign=self.campaign,
            player_name='Test Player',
            character_name='Test Character',
            race='Human',
            character_class='Fighter',
            level=3
        )
        
        self.client = Client()


class CampaignModelTest(BaseTestCase):
    """Test Campaign model functionality"""
    
    def test_campaign_creation(self):
        """Test campaign creation and basic properties"""
        self.assertEqual(self.campaign.title, 'Test Campaign')
        self.assertEqual(self.campaign.description, 'A test campaign for unit testing')
        self.assertEqual(self.campaign.owner, self.user1)
        self.assertIsNotNone(self.campaign.created_at)
    
    def test_campaign_str(self):
        """Test campaign string representation"""
        self.assertEqual(str(self.campaign), 'Test Campaign')
    
    def test_campaign_get_absolute_url(self):
        """Test campaign URL generation"""
        expected_url = reverse('campaigns:campaign_detail', args=[self.campaign.id])
        self.assertEqual(self.campaign.get_absolute_url(), expected_url)
    
    def test_campaign_relationship_with_chapters(self):
        """Test campaign-chapter relationship"""
        self.assertEqual(self.campaign.chapters.count(), 1)
        self.assertEqual(self.campaign.chapters.first(), self.chapter)
    
    def test_campaign_cascade_deletion(self):
        """Test that deleting a campaign deletes related objects"""
        campaign_id = self.campaign.id
        chapter_id = self.chapter.id
        encounter_id = self.encounter.id
        
        self.campaign.delete()
        
        self.assertFalse(Campaign.objects.filter(id=campaign_id).exists())
        self.assertFalse(Chapter.objects.filter(id=chapter_id).exists())
        self.assertFalse(Encounter.objects.filter(id=encounter_id).exists())


class ChapterModelTest(BaseTestCase):
    """Test Chapter model functionality"""
    
    def test_chapter_creation(self):
        """Test chapter creation and basic properties"""
        self.assertEqual(self.chapter.title, 'Test Chapter')
        self.assertEqual(self.chapter.campaign, self.campaign)
        self.assertEqual(self.chapter.order, 1)
        self.assertEqual(self.chapter.status, 'not_started')
        self.assertEqual(self.chapter.level_range, '1-3')
        self.assertFalse(self.chapter.is_optional)
    
    def test_chapter_str(self):
        """Test chapter string representation"""
        expected_str = '1 - Test Chapter (lvl 1-3)'
        self.assertEqual(str(self.chapter), expected_str)
    
    def test_chapter_get_absolute_url(self):
        """Test chapter URL generation"""
        expected_url = reverse('campaigns:chapter_detail', args=[self.chapter.id])
        self.assertEqual(self.chapter.get_absolute_url(), expected_url)
    
    def test_chapter_ordering(self):
        """Test chapter ordering functionality"""
        chapter2 = Chapter.objects.create(
            campaign=self.campaign,
            order=2,
            title='Second Chapter',
            owner=self.user1
        )
        
        chapters = list(Chapter.objects.all())
        self.assertEqual(chapters[0], self.chapter)
        self.assertEqual(chapters[1], chapter2)
    
    def test_chapter_status_choices(self):
        """Test chapter status choices"""
        self.chapter.status = 'in_progress'
        self.chapter.save()
        self.assertEqual(self.chapter.status, 'in_progress')
        
        self.chapter.status = 'completed'
        self.chapter.save()
        self.assertEqual(self.chapter.status, 'completed')
    
    def test_chapter_relationship_with_encounters(self):
        """Test chapter-encounter relationship"""
        self.assertEqual(self.chapter.encounters.count(), 1)
        self.assertEqual(self.chapter.encounters.first(), self.encounter)


class EncounterModelTest(BaseTestCase):
    """Test Encounter model functionality"""
    
    def test_encounter_creation(self):
        """Test encounter creation and basic properties"""
        self.assertEqual(self.encounter.title, 'Test Encounter')
        self.assertEqual(self.encounter.chapter, self.chapter)
        self.assertEqual(self.encounter.type, 'combat')
        self.assertEqual(self.encounter.summary, 'Test encounter summary')
        self.assertEqual(self.encounter.order, 1)
        self.assertFalse(self.encounter.is_optional)
    
    def test_encounter_str(self):
        """Test encounter string representation"""
        expected_str = f'Test Encounter (Chapter {self.chapter.order})'
        self.assertEqual(str(self.encounter), expected_str)
    
    def test_encounter_type_choices(self):
        """Test encounter type choices"""
        types = ['combat', 'social', 'puzzle', 'exploration', 'mixed']
        for encounter_type in types:
            self.encounter.type = encounter_type
            self.encounter.save()
            self.assertEqual(self.encounter.type, encounter_type)
    
    def test_encounter_tags_as_list(self):
        """Test tags parsing functionality"""
        self.encounter.tags = 'combat,dragons,treasure'
        self.encounter.save()
        
        expected_tags = ['combat', 'dragons', 'treasure']
        self.assertEqual(self.encounter.tags_as_list(), expected_tags)
    
    def test_encounter_tags_as_list_empty(self):
        """Test tags parsing with empty tags"""
        self.encounter.tags = ''
        self.encounter.save()
        
        self.assertEqual(self.encounter.tags_as_list(), [''])
    
    def test_encounter_ordering(self):
        """Test encounter ordering within chapters"""
        encounter2 = Encounter.objects.create(
            chapter=self.chapter,
            title='Second Encounter',
            type='social',
            summary='Second encounter summary',
            order=2,
            owner=self.user1
        )
        
        encounters = list(self.chapter.encounters.all())
        self.assertEqual(encounters[0], self.encounter)
        self.assertEqual(encounters[1], encounter2)
    
    def test_encounter_image_upload(self):
        """Test encounter image upload functionality"""
        # Create a simple test image
        test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        
        self.encounter.map_image = test_image
        self.encounter.save()
        
        # Check that an image was uploaded (file name might have a unique suffix)
        self.assertTrue(self.encounter.map_image.name)
        self.assertIn('test_image', self.encounter.map_image.name)


class LocationModelTest(BaseTestCase):
    """Test Location model functionality"""
    
    def test_location_creation(self):
        """Test location creation and basic properties"""
        self.assertEqual(self.location.name, 'Test Location')
        self.assertEqual(self.location.description, 'A test location')
        self.assertEqual(self.location.region, 'Test Region')
        self.assertEqual(self.location.campaign, self.campaign)
        self.assertEqual(self.location.owner, self.user1)
    
    def test_location_str(self):
        """Test location string representation"""
        self.assertEqual(str(self.location), 'Test Location')
    
    def test_location_relationship_with_campaign(self):
        """Test location-campaign relationship"""
        self.assertEqual(self.campaign.locations.count(), 1)
        self.assertEqual(self.campaign.locations.first(), self.location)


class NPCModelTest(BaseTestCase):
    """Test NPC model functionality"""
    
    def test_npc_creation(self):
        """Test NPC creation and basic properties"""
        self.assertEqual(self.npc.name, 'Test NPC')
        self.assertEqual(self.npc.description, 'A test NPC')
        self.assertEqual(self.npc.role, 'merchant')
        self.assertEqual(self.npc.location, self.location)
        self.assertEqual(self.npc.status, 'alive')
        self.assertEqual(self.npc.campaign, self.campaign)
        self.assertEqual(self.npc.owner, self.user1)
    
    def test_npc_str(self):
        """Test NPC string representation"""
        self.assertEqual(str(self.npc), 'Test NPC')
    
    def test_npc_status_choices(self):
        """Test NPC status choices"""
        statuses = ['alive', 'dead', 'missing', 'unknown']
        for status in statuses:
            self.npc.status = status
            self.npc.save()
            self.assertEqual(self.npc.status, status)
    
    def test_npc_location_soft_delete(self):
        """Test NPC location relationship with soft delete"""
        location_id = self.location.id
        self.location.delete()
        
        # Refresh NPC from database
        self.npc.refresh_from_db()
        self.assertIsNone(self.npc.location)
        self.assertFalse(Location.objects.filter(id=location_id).exists())


class CharacterSummaryModelTest(BaseTestCase):
    """Test CharacterSummary model functionality"""
    
    def test_character_creation(self):
        """Test character creation and basic properties"""
        self.assertEqual(self.character.player_name, 'Test Player')
        self.assertEqual(self.character.character_name, 'Test Character')
        self.assertEqual(self.character.race, 'Human')
        self.assertEqual(self.character.character_class, 'Fighter')
        self.assertEqual(self.character.level, 3)
        self.assertEqual(self.character.passive_perception, 10)
        self.assertEqual(self.character.armor_class, 10)
        self.assertEqual(self.character.initiative_modifier, 0)
        self.assertTrue(self.character.alive)
        self.assertFalse(self.character.heroic_inspiration)
    
    def test_character_str(self):
        """Test character string representation"""
        expected_str = 'Test Character (Test Player)'
        self.assertEqual(str(self.character), expected_str)
    
    def test_character_level_validation(self):
        """Test character level constraints"""
        self.character.level = 20
        self.character.save()
        self.assertEqual(self.character.level, 20)
    
    def test_character_combat_stats(self):
        """Test character combat-related statistics"""
        self.character.armor_class = 18
        self.character.current_hit_points = 45
        self.character.initiative_modifier = 3
        self.character.save()
        
        self.assertEqual(self.character.armor_class, 18)
        self.assertEqual(self.character.current_hit_points, 45)
        self.assertEqual(self.character.initiative_modifier, 3)


class SessionNoteModelTest(BaseTestCase):
    """Test SessionNote model functionality"""
    
    def setUp(self):
        super().setUp()
        self.session_note = SessionNote.objects.create(
            encounter=self.encounter,
            date=date.today(),
            content='Test session notes content',
            summary='Test session summary',
            owner=self.user1
        )
    
    def test_session_note_creation(self):
        """Test session note creation and basic properties"""
        self.assertEqual(self.session_note.encounter, self.encounter)
        self.assertEqual(self.session_note.date, date.today())
        self.assertEqual(self.session_note.content, 'Test session notes content')
        self.assertEqual(self.session_note.summary, 'Test session summary')
        self.assertEqual(self.session_note.owner, self.user1)
    
    def test_session_note_str(self):
        """Test session note string representation"""
        expected_str = f'Session on {date.today()} - Test Encounter'
        self.assertEqual(str(self.session_note), expected_str)
    
    def test_session_note_default_date(self):
        """Test session note default date"""
        note = SessionNote.objects.create(
            encounter=self.encounter,
            content='Another test note',
            owner=self.user1
        )
        # Check that the date is today (comparing date parts only)
        self.assertEqual(note.date.date(), date.today())


class ChatMessageModelTest(BaseTestCase):
    """Test ChatMessage model functionality"""
    
    def setUp(self):
        super().setUp()
        self.chat_message = ChatMessage.objects.create(
            campaign=self.campaign,
            role='user',
            content='Test chat message content',
            confirmed_for_chapter=False
        )
    
    def test_chat_message_creation(self):
        """Test chat message creation and basic properties"""
        self.assertEqual(self.chat_message.campaign, self.campaign)
        self.assertEqual(self.chat_message.role, 'user')
        self.assertEqual(self.chat_message.content, 'Test chat message content')
        self.assertFalse(self.chat_message.confirmed_for_chapter)
        self.assertIsNotNone(self.chat_message.created_at)
    
    def test_chat_message_role_choices(self):
        """Test chat message role choices"""
        self.chat_message.role = 'assistant'
        self.chat_message.save()
        self.assertEqual(self.chat_message.role, 'assistant')
    
    def test_chat_message_confirmation(self):
        """Test chat message confirmation functionality"""
        self.chat_message.confirmed_for_chapter = True
        self.chat_message.save()
        self.assertTrue(self.chat_message.confirmed_for_chapter)


class ChapterChatMessageModelTest(BaseTestCase):
    """Test ChapterChatMessage model functionality"""
    
    def setUp(self):
        super().setUp()
        self.chapter_chat_message = ChapterChatMessage.objects.create(
            campaign=self.campaign,
            role='user',
            content='Test chapter chat message content',
            confirmed_for_generation=False
        )
    
    def test_chapter_chat_message_creation(self):
        """Test chapter chat message creation and basic properties"""
        self.assertEqual(self.chapter_chat_message.campaign, self.campaign)
        self.assertEqual(self.chapter_chat_message.role, 'user')
        self.assertEqual(self.chapter_chat_message.content, 'Test chapter chat message content')
        self.assertFalse(self.chapter_chat_message.confirmed_for_generation)
        self.assertIsNotNone(self.chapter_chat_message.created_at)
    
    def test_chapter_chat_message_confirmation(self):
        """Test chapter chat message confirmation functionality"""
        self.chapter_chat_message.confirmed_for_generation = True
        self.chapter_chat_message.save()
        self.assertTrue(self.chapter_chat_message.confirmed_for_generation)


class OwnershipSecurityTest(BaseTestCase):
    """Test ownership and security constraints"""
    
    def test_user_can_only_access_own_campaigns(self):
        """Test that users can only access their own campaigns"""
        user2_campaign = Campaign.objects.create(
            title='User2 Campaign',
            description='A campaign owned by user2',
            owner=self.user2
        )
        
        # Test that user1 can see their own campaign
        user1_campaigns = Campaign.objects.filter(owner=self.user1)
        self.assertEqual(user1_campaigns.count(), 1)
        self.assertEqual(user1_campaigns.first(), self.campaign)
        
        # Test that user2 can see their own campaign
        user2_campaigns = Campaign.objects.filter(owner=self.user2)
        self.assertEqual(user2_campaigns.count(), 1)
        self.assertEqual(user2_campaigns.first(), user2_campaign)
    
    def test_cascade_deletion_on_user_delete(self):
        """Test that deleting a user deletes their campaigns"""
        user_id = self.user1.id
        campaign_id = self.campaign.id
        
        self.user1.delete()
        
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(Campaign.objects.filter(id=campaign_id).exists())
    
    def test_related_objects_ownership(self):
        """Test that all related objects maintain proper ownership"""
        # Objects with direct owner fields should belong to user1
        self.assertEqual(self.campaign.owner, self.user1)
        self.assertEqual(self.chapter.owner, self.user1)
        self.assertEqual(self.encounter.owner, self.user1)
        self.assertEqual(self.location.owner, self.user1)
        self.assertEqual(self.npc.owner, self.user1)
        
        # Objects without owner fields should be related to user1's campaign
        self.assertEqual(self.character.campaign, self.campaign)
        self.assertEqual(self.character.campaign.owner, self.user1)


class LLMIntegrationTest(TestCase):
    """Test LLM integration functionality"""
    
    @patch('campaigns.services.llm.client')
    def test_generate_session_summary(self, mock_client):
        """Test session summary generation with mocked OpenAI client"""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test summary content"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test the function
        bullet_points = "• Players defeated the dragon\n• Found treasure chest\n• Rescued the princess"
        chapter_title = "The Dragon's Lair"
        
        result = generate_session_summary(bullet_points, chapter_title)
        
        # Verify the result
        self.assertEqual(result, "Test summary content")
        
        # Verify the OpenAI client was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        
        self.assertEqual(call_args[1]['model'], 'gpt-3.5-turbo')
        self.assertEqual(call_args[1]['temperature'], 0.7)
        self.assertEqual(call_args[1]['max_tokens'], 500)
        
        # Check that the prompt contains the expected content
        messages = call_args[1]['messages']
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[1]['role'], 'user')
        self.assertIn(bullet_points, messages[1]['content'])
        self.assertIn(chapter_title, messages[1]['content'])
    
    @patch('campaigns.services.llm.client')
    def test_generate_session_summary_no_chapter(self, mock_client):
        """Test session summary generation without chapter title"""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test summary without chapter"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test the function without chapter title
        bullet_points = "• Players explored the dungeon"
        result = generate_session_summary(bullet_points)
        
        # Verify the result
        self.assertEqual(result, "Test summary without chapter")
        
        # Verify the prompt contains "Unknown" for chapter
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        self.assertIn("Unknown", messages[1]['content'])
    
    @patch('campaigns.services.llm.client')
    def test_generate_session_summary_api_error(self, mock_client):
        """Test session summary generation with API error"""
        # Mock an API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Test that the function raises the exception
        with self.assertRaises(Exception):
            generate_session_summary("Test bullet points")


class ModelValidationTest(BaseTestCase):
    """Test model validation and constraints"""
    
    def test_campaign_title_max_length(self):
        """Test campaign title maximum length"""
        long_title = 'x' * 201  # Exceeds max_length=200
        campaign = Campaign(
            title=long_title,
            description='Test description',
            owner=self.user1
        )
        
        with self.assertRaises(Exception):
            campaign.full_clean()
    
    def test_chapter_order_positive_integer(self):
        """Test chapter order accepts zero and positive values"""
        chapter = Chapter(
            campaign=self.campaign,
            order=0,  # PositiveIntegerField allows 0
            title='Test Chapter',
            owner=self.user1
        )
        
        # Should not raise an exception
        chapter.full_clean()
        self.assertEqual(chapter.order, 0)
    
    def test_character_level_positive_integer(self):
        """Test character level accepts zero and positive values"""
        character = CharacterSummary(
            campaign=self.campaign,
            player_name='Test Player',
            character_name='Test Character',
            race='Human',
            level=0  # PositiveIntegerField allows 0
        )
        
        # Should not raise an exception
        character.full_clean()
        self.assertEqual(character.level, 0)
    
    def test_encounter_danger_level_choices(self):
        """Test encounter danger level choices"""
        valid_levels = ['trivial', 'easy', 'medium', 'hard', 'deadly']
        
        for level in valid_levels:
            self.encounter.danger_level = level
            self.encounter.save()
            self.assertEqual(self.encounter.danger_level, level)


class ModelRelationshipTest(BaseTestCase):
    """Test model relationships and foreign keys"""
    
    def test_campaign_to_chapter_relationship(self):
        """Test one-to-many relationship between Campaign and Chapter"""
        # Create additional chapters
        chapter2 = Chapter.objects.create(
            campaign=self.campaign,
            order=2,
            title='Second Chapter',
            owner=self.user1
        )
        
        # Test forward relationship
        self.assertEqual(self.chapter.campaign, self.campaign)
        self.assertEqual(chapter2.campaign, self.campaign)
        
        # Test reverse relationship
        chapters = self.campaign.chapters.all()
        self.assertEqual(chapters.count(), 2)
        self.assertIn(self.chapter, chapters)
        self.assertIn(chapter2, chapters)
    
    def test_chapter_to_encounter_relationship(self):
        """Test one-to-many relationship between Chapter and Encounter"""
        # Create additional encounter
        encounter2 = Encounter.objects.create(
            chapter=self.chapter,
            title='Second Encounter',
            type='social',
            summary='Second encounter summary',
            order=2,
            owner=self.user1
        )
        
        # Test forward relationship
        self.assertEqual(self.encounter.chapter, self.chapter)
        self.assertEqual(encounter2.chapter, self.chapter)
        
        # Test reverse relationship
        encounters = self.chapter.encounters.all()
        self.assertEqual(encounters.count(), 2)
        self.assertIn(self.encounter, encounters)
        self.assertIn(encounter2, encounters)
    
    def test_location_to_npc_relationship(self):
        """Test one-to-many relationship between Location and NPC"""
        # Create additional NPC
        npc2 = NPC.objects.create(
            campaign=self.campaign,
            name='Second NPC',
            location=self.location,
            owner=self.user1
        )
        
        # Test forward relationship
        self.assertEqual(self.npc.location, self.location)
        self.assertEqual(npc2.location, self.location)
        
        # Test reverse relationship (implicit)
        npcs_in_location = NPC.objects.filter(location=self.location)
        self.assertEqual(npcs_in_location.count(), 2)
        self.assertIn(self.npc, npcs_in_location)
        self.assertIn(npc2, npcs_in_location)


class ModelMethodTest(BaseTestCase):
    """Test custom model methods"""
    
    def test_encounter_tags_parsing_with_whitespace(self):
        """Test encounter tags parsing with whitespace"""
        self.encounter.tags = ' combat , dragons , treasure '
        self.encounter.save()
        
        expected_tags = [' combat ', ' dragons ', ' treasure ']
        self.assertEqual(self.encounter.tags_as_list(), expected_tags)
    
    def test_encounter_tags_parsing_single_tag(self):
        """Test encounter tags parsing with single tag"""
        self.encounter.tags = 'combat'
        self.encounter.save()
        
        expected_tags = ['combat']
        self.assertEqual(self.encounter.tags_as_list(), expected_tags)
    
    def test_model_absolute_urls(self):
        """Test all model get_absolute_url methods"""
        # Test Campaign URL
        campaign_url = self.campaign.get_absolute_url()
        expected_campaign_url = reverse('campaigns:campaign_detail', args=[self.campaign.id])
        self.assertEqual(campaign_url, expected_campaign_url)
        
        # Test Chapter URL
        chapter_url = self.chapter.get_absolute_url()
        expected_chapter_url = reverse('campaigns:chapter_detail', args=[self.chapter.id])
        self.assertEqual(chapter_url, expected_chapter_url)