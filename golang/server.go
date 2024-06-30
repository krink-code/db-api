package main

import (
	"database/sql"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
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
	// Define a command-line flag for the port
	portFlag := flag.String("port", "", "port to run the server on")
	flag.Parse()

	// Get the port from the environment variable, if not set use the flag
	port := os.Getenv("PORT")
	if port == "" {
		if *portFlag != "" {
			port = *portFlag
		} else {
			port = "8980"
		}
	}

	router := gin.Default()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())
	router.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Content-Type", "application/json")
	})
	router.Use(extractHeaders())

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

	// Use the specified port
	router.Run(fmt.Sprintf(":%s", port))
}

func extractHeaders() gin.HandlerFunc {
	return func(c *gin.Context) {
		host := c.GetHeader("X-Host")
		if host == "" {
			host = "127.0.0.1"
		}

		port := c.GetHeader("X-Port")
		if port == "" {
			port = "3306"
		}

		database := c.GetHeader("X-Db")

		raiseWarnings := c.GetHeader("X-Raise-Warnings")
		if raiseWarnings == "" {
			raiseWarnings = "true"
		}

		getWarnings := c.GetHeader("X-Get-Warnings")
		if getWarnings == "" {
			getWarnings = "true"
		}

		authPlugin := c.GetHeader("X-Auth-Plugin")
		if authPlugin == "" {
			authPlugin = "mysql_native_password"
		}

		usePure := c.GetHeader("X-Pure")
		if usePure == "" {
			usePure = "true"
		}

		useUnicode := c.GetHeader("X-Unicode")
		if useUnicode == "" {
			useUnicode = "true"
		}

		charset := c.GetHeader("X-Charset")
		if charset == "" {
			charset = "utf8"
		}

		connectionTimeout := c.GetHeader("X-Connection-Timeout")
		if connectionTimeout == "" {
			connectionTimeout = "10"
		}

		c.Set("dbHost", host)
		c.Set("dbPort", port)
		c.Set("dbDatabase", database)
		c.Set("dbRaiseWarnings", raiseWarnings)
		c.Set("dbGetWarnings", getWarnings)
		c.Set("dbAuthPlugin", authPlugin)
		c.Set("dbUsePure", usePure)
		c.Set("dbUseUnicode", useUnicode)
		c.Set("dbCharset", charset)
		c.Set("dbConnectionTimeout", connectionTimeout)

		c.Next()
	}
}

func root(c *gin.Context) {
	c.JSON(http.StatusOK, SQLResponse{Status: http.StatusOK, Message: "OK", Version: version})
}

func showDatabases(c *gin.Context) {
	sql := "SHOW DATABASES"
	rows, err := fetchAll(sql, c)
	if err != nil {
		handleError(c, err)
		return
	}
	c.JSON(http.StatusOK, rows)
}

func showTables(c *gin.Context) {
	database := c.Param("database")
	sql := fmt.Sprintf("SHOW TABLES FROM %s", database)
	rows, err := fetchAll(sql, c)
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

	rows, err := fetchAll(sql, c)
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

	row, err := fetchOne(sql, c)
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

	insertID, err := sqlExec(sql, c, values...)
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

	rowCount, err := sqlExec(sql, c)
	if err != nil {
		handleError(c, err)
		return
	}

	if rowCount > 0 {
		c.JSON(http.StatusOK, SQLResponse{Status: http.StatusOK, Message: "Deleted", Delete: true})
		return
	}

	c.JSON(http.StatusNotFound, SQLResponse{Status: http.StatusNotFound, Message: "Not Found"})
}

func patchOne(c *gin.Context) {
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

	column := c.DefaultQuery("column", "id")

	for key, value := range data {
		sql := fmt.Sprintf("UPDATE %s.%s SET %s='%v' WHERE %s='%s'", database, table, key, value, column, key)
		rowCount, err := sqlExec(sql, c)
		if err != nil {
			handleError(c, err)
			return
		}

		if rowCount > 0 {
			c.JSON(http.StatusOK, SQLResponse{Status: http.StatusOK, Message: "Updated", Update: true})
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

	for key, value := range data {
		sql := fmt.Sprintf("REPLACE INTO %s.%s (%s) VALUES (%v)", database, table, key, value)
		rowCount, err := sqlExec(sql, c)
		if err != nil {
			handleError(c, err)
			return
		}

		if rowCount > 0 {
			c.JSON(http.StatusCreated, SQLResponse{Status: http.StatusCreated, Message: "Created", Update: true})
			return
		}
	}

	c.JSON(http.StatusBadRequest, SQLResponse{Status: http.StatusBadRequest, Message: "Failed Replace", Update: false})
}

func notFound(c *gin.Context) {
	c.JSON(http.StatusNotFound, SQLResponse{Status: http.StatusNotFound, Message: "Not Found"})
}

func handleError(c *gin.Context, err error) {
	c.JSON(http.StatusInternalServerError, SQLResponse{Status: http.StatusInternalServerError, ErrorType: "Internal Server Error", ErrorMessage: err.Error()})
}

func fetchAll(sql string, c *gin.Context) ([]map[string]interface{}, error) {
	user, password, _ := c.Request.BasicAuth()
	db, err := sqlConnection(c, user, password)
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

func fetchOne(sql string, c *gin.Context) (map[string]interface{}, error) {
	user, password, _ := c.Request.BasicAuth()
	db, err := sqlConnection(c, user, password)
	if err != nil {
		return nil, err
	}
	defer db.Close()

	row := db.QueryRow(sql)

	// Prepare a map to store the result
	result := make(map[string]interface{})

	// Use reflection to get column names
	columns, err := getColumns(db, sql)
	if err != nil {
		return nil, err
	}

	// Prepare slices to hold the column values and their pointers
	values := make([]interface{}, len(columns))
	valuePtrs := make([]interface{}, len(columns))
	for i := range columns {
		valuePtrs[i] = &values[i]
	}

	// Scan the result into the value pointers
	if err := row.Scan(valuePtrs...); err != nil {
		return nil, err
	}

	// Convert the scanned values into the result map
	for i, col := range columns {
		val := values[i]
		b, ok := val.([]byte)
		if ok {
			result[col] = string(b)
		} else {
			result[col] = val
		}
	}

	return result, nil
}

func getColumns(db *sql.DB, sql string) ([]string, error) {
	// Execute the query to get the column names
	rows, err := db.Query(sql)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	columns, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	return columns, nil
}

func rowsToMap(rows *sql.Rows) ([]map[string]interface{}, error) {
	columns, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	count := len(columns)
	tableData := make([]map[string]interface{}, 0)
	values := make([]interface{}, count)
	valuePtrs := make([]interface{}, count)

	for rows.Next() {
		for i := range columns {
			valuePtrs[i] = &values[i]
		}

		if err := rows.Scan(valuePtrs...); err != nil {
			return nil, err
		}

		entry := make(map[string]interface{})
		for i, col := range columns {
			var v interface{}
			val := values[i]
			b, ok := val.([]byte)
			if ok {
				v = string(b)
			} else {
				v = val
			}
			entry[col] = v
		}
		tableData = append(tableData, entry)
	}

	return tableData, nil
}

func sqlExec(sql string, c *gin.Context, args ...interface{}) (int64, error) {
	user, password, _ := c.Request.BasicAuth()
	db, err := sqlConnection(c, user, password)
	if err != nil {
		return 0, err
	}
	defer db.Close()

	stmt, err := db.Prepare(sql)
	if err != nil {
		return 0, err
	}
	defer stmt.Close()

	result, err := stmt.Exec(args...)
	if err != nil {
		return 0, err
	}

	return result.RowsAffected()
}

func sqlConnection(c *gin.Context, user string, password string) (*sql.DB, error) {
	host := c.GetString("dbHost")
	port := c.GetString("dbPort")
	database := c.GetString("dbDatabase")
	charset := c.GetString("dbCharset")

	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=%s&parseTime=true&loc=Local", user, password, host, port, database, charset)
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		return nil, err
	}
	return db, nil
}
