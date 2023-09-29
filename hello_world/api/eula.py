class Eula:
    """
    This class is used to create eula endpoints
    """

    # Constructor
    def __init__(self, db_helper, app):
        self.blueprint = Blueprint("eula", __name__)
        self.db_helper = db_helper
        self.app = app
        self.__register_routes()

    # Method used to register routes
    def __register_routes(self):
        self.blueprint.add_url_rule(
            "/provide_eula_consent", view_func=self.__provide_consent, methods=["POST"]
        )

    # Method to update the EULA acceptance
    def __provide_consent(self, **kwargs):
        """
        Arguments :
            email : Email of the user
        Return Type : Success / Failed Message
        """
        try:
            user_email = request.json.get("email")

            if not user_email:
                return (
                    ResponseHelper.return_error("Email id is required", REQUIRED_ERROR),
                    400,
                )

            # Check if we have user already present
            query = "SELECT eulaId FROM EulaConcent WHERE user_id = %s"
            data = (user_email,)
            response = self.db_helper.get_data(query, data)

            # Checking if user has already given consent for older EULA
            if response.json and response.json[0]["eulaId"]:
                query = """UPDATE EulaConcent SET has_consented = %s, consent_date = CURRENT_TIMESTAMP
                           WHERE eulaId = %s"""
                data = (
                    1,
                    response.json[0]["eulaId"],
                )
            else:
                query = "INSERT INTO EulaConcent (user_id) VALUES(%s)"
                data = (user_email,)

            # Saving the consent in EULA
            response = self.db_helper.save_data(query, data)

            if response:
                return ResponseHelper.return_info("Consent submitted successfully"), 200

            return ResponseHelper.return_info("Consent submission failed"), 400

        except Exception as generic_exception:
            self.app.logger.error("Error getting user data : " + str(generic_exception))
            return (
                ResponseHelper.return_error(
                    "Error getting user data", API_FAILED_ERROR
                ),
                500,
            )


"""API for the EULA / Framework Consent"""


# Method to check the EULA acceptance
def is_eula_consented(self, user_email):
    """
    Arguments :
        email : Email of the user
    Return Type : Success / Failed Message
    """
    try:
        if not user_email:
            return False
        # Retrieving EULA Consent
        query = "SELECT * FROM EulaConcent WHERE user_id = %s AND has_consented = %s"
        data = (
            user_email,
            1,
        )
        response = self.db_helper.get_data(
            query, data
        )  # TODO : Call the Core API SQL DB as it has this method already

        if response.json:
            return True

        return False

    except Exception as generic_exception:
        self.app.logger.error(
            "Error getting user data : " + str(generic_exception)
        )  # TODO : Change the logging to either API level loggin or the return statement if its a unique api
        return False


# Method to update the EULA acceptance
def __provide_consent(self, **kwargs):
    """
    Arguments :
        email : Email of the user
    Return Type : Success / Failed Message
    """
    try:
        user_email = event["email"]
        if not user_email:
            return (
                ResponseHelper.return_error("Email id is required", REQUIRED_ERROR),
                400,
            )  # TODO : Response helper is in the privious codebase which is shared.

        # Check if we have user already present
        query = "SELECT eulaId FROM EulaConcent WHERE user_id = %s"
        data = (user_email,)
        response = self.db_helper.get_data(query, data)  # TODO : Call the Core API

        # Checking if user has already given consent for older EULA
        if response.json and response.json[0]["eulaId"]:
            query = """UPDATE EulaConcent SET has_consented = %s, consent_date = CURRENT_TIMESTAMP
                        WHERE eulaId = %s"""
            data = (
                1,
                response.json[0]["eulaId"],
            )
        else:
            query = "INSERT INTO EulaConcent (user_id) VALUES(%s)"
            data = (user_email,)

        # Saving the consent in EULA
        response = self.db_helper.save_data(query, data)  # TODO : Call the Core API
        if response:
            return ResponseHelper.return_info("Consent submitted successfully"), 200
        return ResponseHelper.return_info("Consent submission failed"), 400

    except Exception as generic_exception:
        self.app.logger.error("Error getting user data : " + str(generic_exception))
        return (
            ResponseHelper.return_error("Error getting user data", API_FAILED_ERROR),
            500,
        )
