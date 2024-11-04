package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"services/service-a/src"
	"testing"

	"github.com/stretchr/testify/assert"
)

// Response structure
type Response struct {
	Status string                 `json:"status"`
	Data   map[string]interface{} `json:"data"`
}

// Helper function for setting up services
func setupService() *src.App {
	Service := src.NewDependency()
	return src.NewAppWithDependency(Service)
}

func TestServiceAGetEndpoint(t *testing.T) {
	router := src.NewRouter()

	req, err := http.NewRequest("GET", "/api/resource", nil)
	assert.NoError(t, err)

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)

	expected := `{"status":"success","data":{}}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAGetEndpointWithHeaders(t *testing.T) {
	router := src.NewRouter()

	req, err := http.NewRequest("GET", "/api/resource", nil)
	assert.NoError(t, err)
	req.Header.Set("Authorization", "Bearer token")

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)
	expected := `{"status":"success","data":{}}`
	assert.JSONEq(t, expected, rr.Body.String())

	assert.Equal(t, "Bearer token", req.Header.Get("Authorization"))
}

func TestServiceAGetEndpointWithParams(t *testing.T) {
	router := src.NewRouter()

	req, err := http.NewRequest("GET", "/api/resource?id=123", nil)
	assert.NoError(t, err)

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)

	expected := `{"status":"success","data":{"id":"123"}}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAPostEndpoint(t *testing.T) {
	app := setupService()

	payload := map[string]string{"key": "value"}
	jsonPayload, _ := json.Marshal(payload)

	req, err := http.NewRequest("POST", "/api/resource", bytes.NewBuffer(jsonPayload))
	assert.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	rr := httptest.NewRecorder()
	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusCreated, rr.Code)
	expected := `{"status":"created","data":{"key":"value"}}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAPutEndpoint(t *testing.T) {
	app := setupService()

	payload := map[string]string{"key": "updated_value"}
	jsonPayload, _ := json.Marshal(payload)

	req, err := http.NewRequest("PUT", "/api/resource/123", bytes.NewBuffer(jsonPayload))
	assert.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	rr := httptest.NewRecorder()
	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)
	expected := `{"status":"updated","data":{"key":"updated_value"}}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceADeleteEndpoint(t *testing.T) {
	app := setupService()

	req, err := http.NewRequest("DELETE", "/api/resource/123", nil)
	assert.NoError(t, err)

	rr := httptest.NewRecorder()
	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusNoContent, rr.Code)
}

func TestServiceAWithMultipleDependencies(t *testing.T) {
	ServiceA := src.NewDependency()
	ServiceB := src.NewDependencyB()

	app := src.NewAppWithMultipleDependencies(ServiceA, ServiceB)

	req, err := http.NewRequest("GET", "/api/resource/multi", nil)
	assert.NoError(t, err)

	rr := httptest.NewRecorder()
	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)

	expected := `{"status":"success","data":{"from_service_a":"ok","from_service_b":"ok"}}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAWithInvalidJSONPayload(t *testing.T) {
	app := setupService()

	req, err := http.NewRequest("POST", "/api/resource", bytes.NewBuffer([]byte("{invalid_json}")))
	assert.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	rr := httptest.NewRecorder()
	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusBadRequest, rr.Code)
	expected := `{"status":"error","message":"Invalid JSON"}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAWithMissingHeaders(t *testing.T) {
	app := setupService()

	req, err := http.NewRequest("POST", "/api/resource", nil)
	assert.NoError(t, err)

	rr := httptest.NewRecorder()
	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusUnauthorized, rr.Code)
	expected := `{"status":"error","message":"Authorization required"}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAWithDifferentContentTypes(t *testing.T) {
	app := setupService()

	payload := `<xml><key>value</key></xml>`

	req, err := http.NewRequest("POST", "/api/resource", bytes.NewBuffer([]byte(payload)))
	assert.NoError(t, err)
	req.Header.Set("Content-Type", "application/xml")

	rr := httptest.NewRecorder()
	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusUnsupportedMediaType, rr.Code)
	expected := `{"status":"error","message":"Unsupported content type"}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAPostWithLongProcessingTime(t *testing.T) {
	app := setupService()

	payload := map[string]string{"key": "long_process"}
	jsonPayload, _ := json.Marshal(payload)

	req, err := http.NewRequest("POST", "/api/resource", bytes.NewBuffer(jsonPayload))
	assert.NoError(t, err)

	rr := httptest.NewRecorder()

	// Simulate long processing time
	app.ServeHTTP(rr, req)
	// Use a timeout in production

	assert.Equal(t, http.StatusAccepted, rr.Code)
	expected := `{"status":"accepted","message":"Processing started"}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAWithPagination(t *testing.T) {
	router := src.NewRouter()

	req, err := http.NewRequest("GET", "/api/resource?page=2&limit=10", nil)
	assert.NoError(t, err)

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)

	expected := `{"status":"success","data":{"page":2,"limit":10}}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAWithSearchQuery(t *testing.T) {
	router := src.NewRouter()

	req, err := http.NewRequest("GET", "/api/resource?search=keyword", nil)
	assert.NoError(t, err)

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)

	expected := `{"status":"success","data":{"search":"keyword"}}`
	assert.JSONEq(t, expected, rr.Body.String())
}

func TestServiceAWithPaginationAndSearch(t *testing.T) {
	router := src.NewRouter()

	req, err := http.NewRequest("GET", "/api/resource?page=1&limit=5&search=term", nil)
	assert.NoError(t, err)

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)

	expected := `{"status":"success","data":{"page":1,"limit":5,"search":"term"}}`
	assert.JSONEq(t, expected, rr.Body.String())
}
