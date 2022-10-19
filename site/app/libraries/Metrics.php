<?php

namespace app\libraries;

use app\libraries\database\DatabaseFactory;
use DateTime;
use Exception;

/**
 * Class Metrics
 *
 */
class Metrics
{

    /** This is context information set by WebRouter before the controller for the given route is dispatched. */
    /** @var String */
    private $controller_name = null;
    /** @var String */
    private $method_name = null;

    /** @var Core */
    private $core = null;

    public function __construct($core)
    {
        $this->core = $core;
    }

    /**
     * @param string $identifier
     * An identifier for the specific callsite. For example, log("metric_PDFController_1", )
     * Necessary to easily disambiguate different metrics in a database,
     * Then we can simply check i.e. "WHERE identifier="metric_PDFController_1""
     * Potentially we could autogenerate these in some way, but that would likely be a lot more effort than it is worth.
     * @param $additional_data
     * Array of additional data to log. Will be stored as JSON.
     * @return void
     */
    public function log(string $identifier, $additional_data = null)
    {
        // Capture stack trace information by throwing an exception
        try {
            throw new Exception();
        } catch (Exception $e) {
            $trace = $e->getTrace();
        }
        if ($additional_data === null) {
            $additional_data = array();
        }

        // data to log:
        // - $identifier (type of event)
        // - $additional_data (user-supplied array)
        // - $trace (stack trace)
        // - $controller_name, $method_name (the resolved route)
        // - a timestamp
        // TODO
        // - entire URI ($_SERVER['REQUEST_URI']), however this may include sensitive information (gradeable and grader)

        // TODO: cleanup database connection setup
        // This is more-or-less a hack for now, but it may be as good as we will get
        $db_params_course = $this->core->getConfig()->getSubmittyDatabaseParams();
        $db_params = [
            'dbname' => "submitty_metrics",
            'host' => $db_params_course['host'],
            'port' => $db_params_course['port'],
            'username' => $db_params_course['username'],
            'password' => $db_params_course['password']
        ];
        try {
            // must handle if developer accidentally lets this method be called before much of core is initialized
            // hopefully robust if query fails for a variety of reasons, for example DB or tables non-existent
            $factory = new DatabaseFactory($this->core->getConfig()->getDatabaseDriver());
            $db = $factory->getDatabase($db_params);
            $db->connect();
        } catch (Exception $e) {
            // no logging here since DB may not exist in normal operation, don't want to spam logs
            return;
        }
        try {
            $db->query("
INSERT INTO
    events (timestamp, event_type, controller, method, trace, data)
VALUES
    (now(), ?, ?, ?, ?, ?);
", [$identifier, $this->controller_name, $this->method_name, json_encode($trace), json_encode($additional_data)]);
        } catch (Exception $e) {
            // TODO: appropriate exception type
            // We log this since it means the schema is off, so a logic / programming error.
            Logger::error("metrics query failed");
        }
    }

    public function setEndpoint(string $controller_name, string $method_name)
    {
        $this->controller_name = $controller_name;
        $this->method_name = $method_name;
    }
}

