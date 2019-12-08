# Migrating

Database migrations use the [golang-migrate](https://github.com/golang-migrate/migrate) [cli](https://github.com/golang-migrate/migrate/tree/master/cmd/migrate).
There is release downloads available.

## Up
```
migrate -database postgres://andin_migrate:<PASS>@localhost:5432/andin_dev -path migrations up 1 
```

## Down
```
migrate -database postgres://andin_migrate:<PASS>@localhost:5432/andin_dev -path migrations down 1 
```