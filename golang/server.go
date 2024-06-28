package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/go-sql-driver/mysql"
)

const version = "1.0.0"

type AppJSONEncoder struct{}

func (e AppJSONEncoder) Marshal(v interface{}) ([]byte, error) {
	return json.Marshal(v)
}

type SQLResponse struct {
	Status       int         `json:"status"`
	Message      string      `json:"message"`
	Version      string      `json:"version,omitempty"`
	Insert       bool        `json:"insert,omitempty"`
	RowID        int64       `json:"rowid,omitempty"`
	Update       bool        `json:"update,omitempty"`
	Delete       bool        `json:"delete,omitempty"`
	Rows         interface{} `json:"rows,omitempty"`
	ErrorType    string      `json:"errorType,omitempty"`
	ErrorMessage string      `json:"errorMessage,omitempty"`
	Details      string      `json:"details,omitempty"`
	Method       string      `json:"method,omitempty"`
}

func main() {
	router := gin.Default()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())
	router.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Content-Type", "application/json")
	})

	router.GET("/", root)
	router.GET("/api", showDatabases)
	router.GET("/api/:database", showTables)
	router.GET("/api/:database/:table", getMany)
	router.GET("/api/:database/:table/:key", getOne)
	router.POST("/api", postApi)
	router.POST("/api/:database/:table", postInsert)
	router.DELETE("/api/:database/:table/:key", deleteOne)
	router.PATCH("/api/:database/:table/:key", patchOne)
	router.PUT("/api/:database/:table", putReplace)

	router.NoRoute(notFound)

	router.Run(":8980")
}

func root(c *gin.Context) {
	c.JSON(http.StatusOK, SQLResponse{Status: http.StatusOK, Message: "OK", Version: version})
}

func showDatabases(c *gin.Context) {
	sql := "SHOW DATABASES"
	rows, err := fetchAll(sql)
	if err != nil {
		handleError(c, err)
		return
	}
	c.JSON(http.StatusOK, rows)
}

func showTables(c *gin.Context) {
	database := c.Param("database")
	sql := fmt.Sprintf("SHOW TABLES FROM %s", database)
	rows, err := fetchAll(sql)
	if err != nil {
		handleError(c, err)
		return
	}
	c.JSON(http.StatusOK, rows)
}

func getMany(c *gin.Context) {
	database := c.Param("database")
	table := c.Param("table")

	fields := c.DefaultQuery("fields", "*")
	limit := c.Query("limit")

	var sql string
	if len(c.Request.URL.Query()) == 0 {
		sql = fmt.Sprintf("SHOW FIELDS FROM %s.%s", database, table)
	} else {
		sql = fmt.Sprintf("SELECT %s FROM %s.%s", fields, database, table)
	}

	if limit != "" {
		sql += " LIMIT " + limit
	}

	rows, err := fetchAll(sql)
	if err != nil {
		handleError(c, err)
		return
	}

	if rows != nil {
		c.JSON(http.StatusOK, rows)
		return
	}
	c.JSON(http.StatusNotFound, SQLResponse{Status: http.StatusNotFound, Message: "Not Found"})
}

func getOne(c *gin.Context) {
	database := c.Param("database")
	table := c.Param("table")
	key := c.Param("key")

	fields := c.DefaultQuery("fields", "*")
	column := c.DefaultQuery("column", "id")

	sql := fmt.Sprintf("SELECT %s FROM %s.%s WHERE %s='%s'", fields, database, table, column, key)

	row, err := fetchOne(sql)
	if err != nil {
		handleError(c, err)
		return
	}

	if row != nil {
		c.JSON(http.StatusOK, row)
		return
	}
	c.JSON(http.StatusNotFound, SQLResponse{Status: http.StatusNotFound, Message: "Not Found"})
}

func postApi(c *gin.Context) {
	if c.ContentType() != "" {
		c.JSON(http.StatusUnsupportedMediaType, SQLResponse{Status: http.StatusUnsupportedMediaType, Method: "POST"})
		return
	}
	c.JSON(http.StatusUnsupportedMediaType, SQLResponse{Status: http.StatusUnsupportedMediaType, Method: "POST"})
}

func postInsert(c *gin.Context) {
	database := c.Param("database")
	table := c.Param("table")

	var data map[string]interface{}
	if err := c.BindJSON(&data); err != nil {
		handleError(c, err)
		return
	}

	fields := []string{}
	values := []interface{}{}
	placeholders := []string{}

	for k, v := range data {
		fields = append(fields, k)
		values = append(values, v)
		placeholders = append(placeholders, "?")
	}

	sql := fmt.Sprintf("INSERT INTO %s.%s (%s) VALUES (%s)", database, table, strings.Join(fields, ","), strings.Join(placeholders, ","))

	insertID, err := sqlExec(sql, values...)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusCreated, SQLResponse{Status: http.StatusCreated, Message: "Created", Insert: true, RowID: insertID})
}

func deleteOne(c *gin.Context) {
	database := c.Param("database")
	table := c.Param("table")
	key := c.Param("key")

	column := c.DefaultQuery("column", "id")

	sql := fmt.Sprintf("DELETE FROM %s.%s WHERE %s='%s'", database, table, column, key)

	rowCount, err := sqlExec(sql)
	if err != nil {
		handleError(c, err)
		return
	}

	if rowCount > 0 {
		c.JSON(http.StatusOK, SQLResponse{Status: http.StatusOK, Message: "Deleted", Delete: true})
		return
	}
	c.JSON(http.StatusBadRequest, SQLResponse{Status: http.StatusBadRequest, Message: "Failed Delete", Delete: false})
}

func patchOne(c *gin.Context) {
	database := c.Param("database")
	table := c.Param("table")
	key := c.Param("key")

	column := c.DefaultQuery("column", "id")

	if c.ContentType() != "application/json" {
		c.JSON(http.StatusPreconditionFailed, SQLResponse{Status: http.StatusPreconditionFailed, ErrorType: "Precondition Failed"})
		return
	}

	var data map[string]interface{}
	if err := c.BindJSON(&data); err != nil {
		handleError(c, err)
		return
	}

	if len(data) > 1 {
		c.JSON(http.StatusMethodNotAllowed, SQLResponse{Status: http.StatusMethodNotAllowed, ErrorType: "Method Not Allowed", ErrorMessage: "Single Key-Value Only", Update: false})
		return
	}

	for field, value := range data {
		sql := fmt.Sprintf("UPDATE %s.%s SET %s='%v' WHERE %s='%s'", database, table, field, value, column, key)
		rowCount, err := sqlExec(sql)
		if err != nil {
			handleError(c, err)
			return
		}

		if rowCount > 0 {
			c.JSON(http.StatusCreated, SQLResponse{Status: http.StatusCreated, Message: "Created", Update: true})
			return
		}
	}

	c.JSON(http.StatusBadRequest, SQLResponse{Status: http.StatusBadRequest, Message: "Failed Update", Update: false})
}

func putReplace(c *gin.Context) {
	database := c.Param("database")
	table := c.Param("table")

	if c.ContentType() != "application/json" {
		c.JSON(http.StatusPreconditionFailed, SQLResponse{Status: http.StatusPreconditionFailed, ErrorType: "Precondition Failed"})
		return
	}

	var data map[string]interface{}
	if err := c.BindJSON(&data); err != nil {
		handleError(c, err)
		return
	}

	fields := []string{}
	values := []interface{}{}
	placeholders := []string{}

	for k, v := range data {
		fields = append(fields, k)
		values = append(values, v)
		placeholders = append(placeholders, "?")
	}

	sql := fmt.Sprintf("REPLACE INTO %s.%s (%s) VALUES (%s)", database, table, strings.Join(fields, ","), strings.Join(placeholders, ","))

	insertID, err := sqlExec(sql, values...)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusCreated, SQLResponse{Status: http.StatusCreated, Message: "Created", Insert: true, RowID: insertID})
}

func notFound(c *gin.Context) {
	c.JSON(http.StatusNotFound, SQLResponse{Status: http.StatusNotFound, ErrorType: "Not Found", Message: "Not Found"})
}

func handleError(c *gin.Context, err error) {
	c.JSON(http.StatusInternalServerError, SQLResponse{Status: http.StatusInternalServerError, ErrorType: "Internal Server Error", ErrorMessage: err.Error()})
}

func fetchAll(sql string) ([]map[string]interface{}, error) {
	db, err := sqlConnection()
	if err != nil {
		return nil, err
	}
	defer db.Close()

	rows, err := db.Query(sql)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return rowsToMap(rows)
}

func fetchOne(sql string) (map[string]interface{}, error) {
	db, err := sqlConnection()
	if err != nil {
		return nil, err
	}
	defer db.Close()

	row := db.QueryRow(sql)

	// To fetch a single row, we need to know the columns in advance
	columns := []string{"id", "name"} // example columns
	values := make([]interface{}, len(columns))
	valuePtrs := make([]interface{}, len(columns))
	for i := range columns {
		valuePtrs[i] = &values[i]
	}

	if err := row.Scan(valuePtrs...); err != nil {
		return nil, err
	}

	result := make(map[string]interface{})
	for i, col := range columns {
		result[col] = values[i]
	}

	return result, nil
}

func sqlExec(sql string, args ...interface{}) (int64, error) {
	db, err := sqlConnection()
	if err != nil {
		return 0, err
	}
	defer db.Close()

	result, err := db.Exec(sql, args...)
	if err != nil {
		return 0, err
	}

	if strings.HasPrefix(sql, "INSERT") {
		return result.LastInsertId()
	}

	return result.RowsAffected()
}

func rowsToMap(rows *sql.Rows) ([]map[string]interface{}, error) {
	columns, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	var result []map[string]interface{}
	for rows.Next() {
		values := make([]interface{}, len(columns))
		valuePtrs := make([]interface{}, len(columns))
		for i := range columns {
			valuePtrs[i] = &values[i]
		}

		if err := rows.Scan(valuePtrs...); err != nil {
			return nil, err
		}

		row := make(map[string]interface{})
		for i, col := range columns {
			row[col] = values[i]
		}

		result = append(result, row)
	}

	return result, rows.Err()
}

func sqlConnection() (*sql.DB, error) {
	db, err := sql.Open("mysql", "user:password@tcp(127.0.0.1:3306)/")
	if err != nil {
		return nil, err
	}
	return db, nil
}
