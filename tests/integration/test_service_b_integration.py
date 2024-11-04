import unittest
import requests
from unittest.mock import patch
import json

class TestServiceBIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://service-b:8080/api"
        cls.headers = {"Content-Type": "application/json"}
    
    def test_health_check(self):
        url = f"{self.base_url}/health"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'healthy')
    
    @patch('requests.post')
    def test_post_data(self, mock_post):
        url = f"{self.base_url}/data"
        data = {"id": 123, "name": "Test Name"}
        expected_response = {"message": "Data created successfully", "status": "created"}
        
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = expected_response
        
        response = requests.post(url, data=json.dumps(data), headers=self.headers)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), expected_response)
        mock_post.assert_called_once_with(url, data=json.dumps(data), headers=self.headers)
    
    @patch('requests.get')
    def test_get_data(self, mock_get):
        url = f"{self.base_url}/data/123"
        expected_response = {"id": 123, "name": "Test Name", "status": "active"}
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = expected_response
        
        response = requests.get(url, headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)
        mock_get.assert_called_once_with(url, headers=self.headers)
    
    @patch('requests.delete')
    def test_delete_data(self, mock_delete):
        url = f"{self.base_url}/data/123"
        expected_response = {"message": "Data deleted successfully", "status": "deleted"}
        
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.json.return_value = expected_response
        
        response = requests.delete(url, headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)
        mock_delete.assert_called_once_with(url, headers=self.headers)
    
    @patch('requests.put')
    def test_update_data(self, mock_put):
        url = f"{self.base_url}/data/123"
        data = {"name": "Updated Name"}
        expected_response = {"message": "Data updated successfully", "status": "updated"}
        
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = expected_response
        
        response = requests.put(url, data=json.dumps(data), headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)
        mock_put.assert_called_once_with(url, data=json.dumps(data), headers=self.headers)
    
    def test_integration_with_external_service(self):
        url = f"{self.base_url}/external-integration"
        response = requests.get(url, headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('external_status', response.json())
        self.assertEqual(response.json()['external_status'], 'integrated')
    
    @patch('requests.post')
    def test_data_processing(self, mock_post):
        url = f"{self.base_url}/process"
        data = {"input": "Test Input"}
        expected_response = {"output": "Processed Output", "status": "success"}
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_response
        
        response = requests.post(url, data=json.dumps(data), headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)
        mock_post.assert_called_once_with(url, data=json.dumps(data), headers=self.headers)
    
    def test_database_interaction(self):
        url = f"{self.base_url}/database/interaction"
        response = requests.get(url, headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('db_status', response.json())
        self.assertEqual(response.json()['db_status'], 'connected')

    @patch('requests.post')
    def test_file_upload(self, mock_post):
        url = f"{self.base_url}/upload"
        file_data = {'file': ('test_file.txt', 'file content')}
        expected_response = {"message": "File uploaded successfully", "status": "success"}
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_response
        
        response = requests.post(url, files=file_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)
        mock_post.assert_called_once_with(url, files=file_data)
    
    @patch('requests.get')
    def test_get_metrics(self, mock_get):
        url = f"{self.base_url}/metrics"
        expected_response = {"uptime": 3600, "request_count": 1024}
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = expected_response
        
        response = requests.get(url, headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)
        mock_get.assert_called_once_with(url, headers=self.headers)
    
    def test_service_timeout(self):
        url = f"{self.base_url}/timeout"
        with self.assertRaises(requests.exceptions.Timeout):
            requests.get(url, timeout=0.001)
    
    @patch('requests.post')
    def test_data_processing_timeout(self, mock_post):
        url = f"{self.base_url}/process"
        data = {"input": "Test Input"}
        
        mock_post.side_effect = requests.exceptions.Timeout
        
        with self.assertRaises(requests.exceptions.Timeout):
            requests.post(url, data=json.dumps(data), headers=self.headers)

if __name__ == '__main__':
    unittest.main()