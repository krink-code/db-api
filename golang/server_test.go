package main

import (
	"encoding/base64"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestRoot(t *testing.T) {
	router := gin.Default()
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  200,
			"message": "OK",
			"version": "1.0.0",
		})
	})

	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	expected := `{"message":"OK","status":200,"version":"1.0.0"}`
	if rr.Body.String() != expected {
		t.Errorf("handler returned unexpected body: got %v want %v",
			rr.Body.String(), expected)
	}
}

func TestShowDatabases(t *testing.T) {
	router := gin.Default()

	router.GET("/api", showDatabases)

	// Encode the username and password in base64
	username := `dbuser`
	password := `dbpass`
	auth := username + ":" + password
	encodedAuth := base64.StdEncoding.EncodeToString([]byte(auth))

	req, err := http.NewRequest("GET", "/api", nil)
	if err != nil {
		t.Fatal(err)
	}

	// Set the Authorization header
	req.Header.Set("Authorization", "Basic "+encodedAuth)

	rr := httptest.NewRecorder()

	router.ServeHTTP(rr, req)
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Add your assertions for the response body here
}

func TestShowTables(t *testing.T) {
	router := gin.Default()
	router.GET("/api/:database", showTables)

	req, err := http.NewRequest("GET", "/api/testdb", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Add your assertions for the response body here
}

func TestGetMany(t *testing.T) {
	router := gin.Default()
	router.GET("/api/:database/:table", getMany)

	req, err := http.NewRequest("GET", "/api/testdb/testtable", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Add your assertions for the response body here
}

func TestGetOne(t *testing.T) {
	router := gin.Default()
	router.GET("/api/:database/:table/:key", getOne)

	req, err := http.NewRequest("GET", "/api/testdb/testtable/1", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Add your assertions for the response body here
}

func TestPostApi(t *testing.T) {
	router := gin.Default()
	router.POST("/api", postApi)

	req, err := http.NewRequest("POST", "/api", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusUnsupportedMediaType {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusUnsupportedMediaType)
	}

	// Add your assertions for the response body here
}

func TestPostInsert(t *testing.T) {
	router := gin.Default()
	router.POST("/api/:database/:table", postInsert)

	req, err := http.NewRequest("POST", "/api/testdb/testtable", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusCreated {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusCreated)
	}

	// Add your assertions for the response body here
}

func TestDeleteOne(t *testing.T) {
	router := gin.Default()
	router.DELETE("/api/:database/:table/:key", deleteOne)

	req, err := http.NewRequest("DELETE", "/api/testdb/testtable/1", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Add your assertions for the response body here
}

func TestPatchOne(t *testing.T) {
	router := gin.Default()
	router.PATCH("/api/:database/:table/:key", patchOne)

	req, err := http.NewRequest("PATCH", "/api/testdb/testtable/1", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Add your assertions for the response body here
}

func TestPutReplace(t *testing.T) {
	router := gin.Default()
	router.PUT("/api/:database/:table", putReplace)

	req, err := http.NewRequest("PUT", "/api/testdb/testtable", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusCreated {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusCreated)
	}

	// Add your assertions for the response body here
}

func TestNotFound(t *testing.T) {
	router := gin.Default()
	router.NoRoute(notFound)

	req, err := http.NewRequest("GET", "/notfound", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusNotFound {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusNotFound)
	}

	// Add your assertions for the response body here
}
