
WITH data_source_result AS (
    WITH survey_result AS (
        INSERT INTO survey (surveyor, external)
        VALUES
            ('Test Surveyor abc', False)
        RETURNING id
    )
    INSERT INTO data_source (survey, import_date)
        VALUES
            ((SELECT id FROM survey_result), NOW())
        RETURNING id
)
INSERT INTO room (level, geometry, data_source)
    VALUES
        (0, (
            SELECT ST_GeomFromText('POLYGON((-71.1776585052917 42.3902909739571,-71.1776820268866 42.3903701743239,
-71.1776063012595 42.3903825660754,-71.1775826583081 42.3903033653531,-71.1776585052917 42.3902909739571))')
        ), (SELECT id FROM data_source_result))
    RETURNING id;