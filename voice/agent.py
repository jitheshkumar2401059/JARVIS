import logging

from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    cli,
    function_tool,
)

from livekit.plugins import google

from tools.weather import get_weather
from tools.location import find_saved_location, save_location
from tools.websearch import web_search
from tools.computer import open_application


load_dotenv()

logging.basicConfig(level=logging.INFO)

server = AgentServer()


class Jarvis(Agent):

    def __init__(self) -> None:

        # Stores a newly discovered location
        # while waiting for user confirmation.
        self.pending_location = None

        # Stores a possible fuzzy spelling match
        # while waiting for user confirmation.
        self.pending_match = None

        super().__init__(
            instructions="""
You are JARVIS, a highly intelligent personal AI assistant.

Your personality:
- Calm
- Professional
- Helpful
- Intelligent
- Concise

Speak naturally and clearly.
Address the user as Sir when appropriate.

Do not claim to have performed an action unless you actually performed it.

WEATHER AND LOCATION RULES:

1. For a normal known location:
   - Use the weather tool.
   - Give the weather result to the user.

2. For a possible spelling match:
   - If the weather tool returns status "possible_match",
     DO NOT silently assume the location is correct.
   - Ask the user:
     "Did you mean <suggested location>?"
   - Wait for confirmation.

   - If the user clearly confirms with:
     "yes", "correct", "that's right", "exactly",
     or a similar confirmation, immediately call:

     confirm_location(location_name="<suggested location>")

   - Example:
     Assistant: "Did you mean Mulligoor?"
     User: "Yes."
     → Call confirm_location(location_name="Mulligoor")

   - Do not ask the user to repeat the location name.
   - Do not call save_confirmed_location for a fuzzy match.

   - If the user says "no", do not use the suggested location.
     Ask for a nearby town, city, village, district, or state
     and search again.

3. For an unknown location:
   - Never guess.
   - Ask the user for a nearby town, city, village, district,
     or state.
   - Use the additional context to search again.

4. If a new location is successfully resolved:
   - Tell the user exactly which location was found.
   - Ask for confirmation before saving it.
   - Do NOT save it automatically.

5. Only call save_confirmed_location after the user clearly
   confirms with words such as:
   "yes", "correct", "that's right", "save it", or similar.

6. Existing saved locations must NOT be saved again.

7. A fuzzy match is already an existing saved location.
   Confirmation only selects the correct saved location.
   It does not create another JSON entry.

8. If the user says no to a possible match:
   - Do not use the suggested location.
   - Ask for more location context.

9. Never claim a location was saved unless the save tool
   actually succeeds.

WEB SEARCH RULES:

10. Use web_search_tool when the user asks for:
    - Latest or current information
    - Recent news or events
    - Today's information
    - Current prices, releases, updates, or developments
    - Information that may have changed recently
    - Information you are uncertain about and should verify online

11. For basic and stable questions that you can answer confidently,
    answer directly without using web_search_tool.

12. Examples of questions that normally do NOT require web search:
    - What is a CPU?
    - What is RAM?
    - What is Python?
    - What is a linked list?
    - Explain binary search.
    - What is an operating system?

13. If the user explicitly says "search the web",
    "search online", "look it up", or similar,
    always use web_search_tool.

14. Do not use web_search_tool simply because a question is
    phrased as "What is..." or "Explain...".

15. After receiving search results, use the relevant information
    to answer the user's question clearly and concisely.
COMPUTER CONTROL RULES:

16. Use open_application_tool when the user asks you to open
    an application on the Mac.

17. Only request applications that are allowed by the computer
    control tool.

18. Do not claim an application was opened unless the tool
    reports success.
"""
        )

    @function_tool
    async def weather(
        self,
        place: str,
        nearby: str = None,
        district: str = None,
        state: str = None,
    ):
        """
        Get the current weather for a location.
        """

        result = get_weather(
            place=place,
            nearby=nearby,
            district=district,
            state=state,
        )

        # -------------------------------------------------
        # Possible spelling match
        # -------------------------------------------------

        if result.get("status") == "possible_match":

            self.pending_match = {
                "name": result["suggested_location"],
                "district": result.get("district"),
                "state": result.get("state"),
                "country": result.get("country"),
            }

            return result

        # -------------------------------------------------
        # Newly discovered location
        # -------------------------------------------------

        if (
            result.get("status") == "success"
            and result.get("should_save")
        ):

            self.pending_location = {
                "name": result["location"],
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "district": district,
                "state": state,
                "country": "India",
            }

        return result

    @function_tool
    async def confirm_location(self, location_name: str):
        """
        Confirm a possible spelling match and get its weather.

        Use this tool when the user explicitly confirms a suggested
        location, for example:
        "Yes", "correct", "that's right", or "yes, Mulligoor".

        location_name must be the suggested saved location name.
        """

        # Verify that there is actually a pending fuzzy match.
        if not self.pending_match:
            return {
                "success": False,
                "message": "There is no location waiting for confirmation.",
            }

        suggested_name = self.pending_match["name"]

        # Make sure the confirmed name matches the suggestion.
        if location_name.strip().lower() != suggested_name.strip().lower():
            return {
                "success": False,
                "message": (
                    f"The pending suggested location is "
                    f"{suggested_name}."
                ),
            }

        # Get the actual saved location.
        location = find_saved_location(suggested_name)

        if not location:
            self.pending_match = None

            return {
                "success": False,
                "message": (
                    f"I could not retrieve the saved location "
                    f"{suggested_name}."
                ),
            }

        # Clear the pending match.
        self.pending_match = None

        # Get weather using the confirmed saved location.
        result = get_weather(suggested_name)

        return {
            "success": True,
            "location": suggested_name,
            "message": f"Confirmed {suggested_name}.",
            "weather": result,
        }
    @function_tool
    async def save_confirmed_location(self):
        """
        Save a newly discovered location after explicit
        user confirmation.
        """

        if not self.pending_location:
            return {
                "success": False,
                "message": (
                    "There is no new location waiting "
                    "for confirmation."
                ),
            }

        location = self.pending_location

        try:
            save_location(
                name=location["name"],
                latitude=location["latitude"],
                longitude=location["longitude"],
                district=location["district"],
                state=location["state"],
                country=location["country"],
            )

            saved_name = location["name"]

            # Clear pending location after successful save.
            self.pending_location = None

            return {
                "success": True,
                "message": (
                    f"{saved_name} has been saved successfully."
                ),
            }

        except Exception as error:

            return {
                "success": False,
                "message": (
                    f"I could not save the location: {error}"
                ),
            }
    @function_tool
    async def open_application_tool(self, application: str):
        """
        Open an approved macOS application.

        Only applications allowed by the computer control
        security policy can be opened.
        """
        return open_application(application)
    @function_tool
    async def web_search_tool(self, query: str):
        """
        Search the web for current information.
        """

        return web_search(query)
@server.rtc_session(agent_name="jarvis")
async def entrypoint(ctx: JobContext):

    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-3.1-flash-live-preview",
            voice="Puck",
        ),
    )

    await session.start(
        room=ctx.room,
        agent=Jarvis(),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions=(
            "Greet the user as JARVIS and ask how you can help."
        )
    )


if __name__ == "__main__":
    cli.run_app(server)
