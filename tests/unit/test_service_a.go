package unit

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"services/service-a/src"
)

// Data for tests
var mockData = `{
    "name": "Test",
    "value": "1234"
}`

// Test Handler for HTTP GET
func TestGetHandler(t *testing.T) {
	req, err := http.NewRequest("GET", "/api/v1/resource", nil)
	if err != nil {
		t.Fatalf("Could not create request: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.GetHandler)

	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("Expected status OK; got %v", rr.Code)
	}

	expected := `{"message":"Resource fetched successfully"}`
	if rr.Body.String() != expected {
		t.Errorf("Expected %v; got %v", expected, rr.Body.String())
	}
}

// Test Handler for HTTP POST
func TestPostHandler(t *testing.T) {
	req, err := http.NewRequest("POST", "/api/v1/resource", strings.NewReader(mockData))
	if err != nil {
		t.Fatalf("Could not create request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.PostHandler)

	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusCreated {
		t.Errorf("Expected status Created; got %v", rr.Code)
	}

	responseData, err := ioutil.ReadAll(rr.Body)
	if err != nil {
		t.Fatalf("Could not read response: %v", err)
	}

	var result map[string]string
	err = json.Unmarshal(responseData, &result)
	if err != nil {
		t.Fatalf("Could not unmarshal response: %v", err)
	}

	if result["message"] != "Resource created successfully" {
		t.Errorf("Unexpected response message: %v", result["message"])
	}
}

// Test Handler for HTTP PUT
func TestPutHandler(t *testing.T) {
	req, err := http.NewRequest("PUT", "/api/v1/resource/1", strings.NewReader(mockData))
	if err != nil {
		t.Fatalf("Could not create request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.PutHandler)

	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("Expected status OK; got %v", rr.Code)
	}

	responseData, err := ioutil.ReadAll(rr.Body)
	if err != nil {
		t.Fatalf("Could not read response: %v", err)
	}

	var result map[string]string
	err = json.Unmarshal(responseData, &result)
	if err != nil {
		t.Fatalf("Could not unmarshal response: %v", err)
	}

	if result["message"] != "Resource updated successfully" {
		t.Errorf("Unexpected response message: %v", result["message"])
	}
}

// Test Handler for HTTP DELETE
func TestDeleteHandler(t *testing.T) {
	req, err := http.NewRequest("DELETE", "/api/v1/resource/1", nil)
	if err != nil {
		t.Fatalf("Could not create request: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.DeleteHandler)

	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("Expected status OK; got %v", rr.Code)
	}

	expected := `{"message":"Resource deleted successfully"}`
	if rr.Body.String() != expected {
		t.Errorf("Expected %v; got %v", expected, rr.Body.String())
	}
}

// Test Error Scenario for HTTP POST (Invalid Payload)
func TestPostHandlerInvalidPayload(t *testing.T) {
	invalidData := `{"invalid":"data"}`
	req, err := http.NewRequest("POST", "/api/v1/resource", strings.NewReader(invalidData))
	if err != nil {
		t.Fatalf("Could not create request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.PostHandler)

	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusBadRequest {
		t.Errorf("Expected status BadRequest; got %v", rr.Code)
	}

	expected := `{"error":"Invalid payload"}`
	if rr.Body.String() != expected {
		t.Errorf("Expected %v; got %v", expected, rr.Body.String())
	}
}

// Test Service Logic for FetchResource
func TestFetchResource(t *testing.T) {
	result, err := src.FetchResource(1)
	if err != nil {
		t.Fatalf("Error occurred: %v", err)
	}

	if result.Name != "TestResource" {
		t.Errorf("Expected resource name 'TestResource'; got %v", result.Name)
	}

	if result.Value != "Value123" {
		t.Errorf("Expected resource value 'Value123'; got %v", result.Value)
	}
}

// Test Service Logic for CreateResource
func TestCreateResource(t *testing.T) {
	resource := src.Resource{
		Name:  "NewResource",
		Value: "4567",
	}

	result, err := src.CreateResource(resource)
	if err != nil {
		t.Fatalf("Error occurred: %v", err)
	}

	if result.Name != resource.Name {
		t.Errorf("Expected resource name '%v'; got %v", resource.Name, result.Name)
	}

	if result.Value != resource.Value {
		t.Errorf("Expected resource value '%v'; got %v", resource.Value, result.Value)
	}
}

// Test Service Logic for UpdateResource
func TestUpdateResource(t *testing.T) {
	resource := src.Resource{
		Name:  "UpdatedResource",
		Value: "9999",
	}

	result, err := src.UpdateResource(1, resource)
	if err != nil {
		t.Fatalf("Error occurred: %v", err)
	}

	if result.Name != resource.Name {
		t.Errorf("Expected updated name '%v'; got %v", resource.Name, result.Name)
	}

	if result.Value != resource.Value {
		t.Errorf("Expected updated value '%v'; got %v", resource.Value, result.Value)
	}
}

// Test Service Logic for DeleteResource
func TestDeleteResource(t *testing.T) {
	err := src.DeleteResource(1)
	if err != nil {
		t.Fatalf("Error occurred: %v", err)
	}

	// Try fetching the resource again to ensure it is deleted
	_, fetchErr := src.FetchResource(1)
	if fetchErr == nil {
		t.Errorf("Expected error; got none after deletion")
	}
}

// Test Fetching Non-existent Resource
func TestFetchNonExistentResource(t *testing.T) {
	_, err := src.FetchResource(999)
	if err == nil {
		t.Errorf("Expected error for non-existent resource; got none")
	}
}
