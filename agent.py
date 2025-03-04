import warnings
warnings.filterwarnings('ignore')
import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel
from typing import Optional
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to access backend

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'

# Initialize search tool
search_tool = SerperDevTool()

#address = input("Enter the property address: ")
@app.route('/api/property', methods=['GET'])
def get_property():
    # Get address from the query parameter
    address = request.args.get('address')
    if address:
        # Function to generate Redfin URL
        def get_redfin_url(address: str):
            base_url = "https://www.redfin.com/"
            search_url = f"{base_url}search#query={address.replace(' ', '%20')}"
            return search_url
    
        # Scrape property details from Redfin
        docs_scrape_tool = ScrapeWebsiteTool(
            website_url=get_redfin_url(address)
        )
        
        # Real Estate Data Specialist Agent
        real_estate_agent = Agent(
            role="Real Estate Data Specialist",
            goal="Retrieve and provide accurate property information based on {address}",
            backstory="You are an expert in real estate data analysis with access to comprehensive property databases.",
            verbose=True,
            allow_delegation=False
        )
        
        # Real Estate Data Verification Assistant Agent
        assistant_agent = Agent(
            role="Real Estate Data Verification Assistant",
            goal="Verify and cross-check property information and market analysis provided by the Real Estate Data Specialist and Nearby Amenities Finder",
            backstory="""You are an AI assistant specializing in real estate data verification and quality control. Your primary responsibilities include:
                        1. Double-checking property information and market trend data for accuracy.
                        2. Verifying calculations and predictions made by the AI Real Estate Market Analyst.
                        3. Cross-referencing information with multiple reliable sources to ensure data integrity.
                        4. Flagging any discrepancies or potential errors in the analysis for further review.
                        5. Providing additional context or supplementary information to enhance the main analysis.
                        6. Ensuring that all recommendations align with current market conditions and regulatory requirements.
                        """,
            verbose=True,
            allow_delegation=False,
            tools=[search_tool, docs_scrape_tool]  # Tools for verifying and retrieving data
        )
        
        # Nearby Amenities Finder Agent
        amenities_finder_agent = Agent(
            role="Nearby Amenities Finder",
            goal="Identify and list the nearest day-to-day amenities along with their distances from the given property address.",
            backstory="""You specialize in finding nearby essential services such as grocery stores, hospitals, pharmacies, gyms, and restaurants.
                         Your job is to scrape online sources like Google Maps, Yelp, and OpenStreetMap to fetch accurate location and distance data.""",
            verbose=True,
            allow_delegation=False,
        )
        
        # Task for finding nearby amenities
        find_nearby_amenities_task = Task(
            description="Scrape websites to find the nearest day-to-day amenities for the property at {address}. "
                        "Identify locations and distances for:\n"
                        "- Grocery stores\n"
                        "- Hospitals\n"
                        "- Pharmacies\n"
                        "- Gyms\n"
                        "- Restaurants\n"
                        "Use sources like Google Maps, Yelp, and OpenStreetMap. Ensure accuracy in distances and locations.",
            expected_output="A structured JSON object listing the top 5 nearest amenities in each category with their distance from the property.",
            agent=amenities_finder_agent,
            tools=[search_tool],
        )
        
        # Define PropertyDetails Pydantic model
        class PropertyDetails(BaseModel):
            address: str
            price_current: str
            number_of_bedrooms: int
            number_of_bathrooms: int
            square_footage: str
            property_type: str
            property_taxes: str
            nearby_schools: dict
            local_crime_rates: Optional[str]
            proximity_to_police_stations: Optional[str]
            recent_sales_of_similar_properties: Optional[str]
            nearby_public_transport: dict
            hoa_fees: str
            rental_value_estimate: Optional[str]
        
        
        
        # Task to fetch property details
        property_details_task = Task(
            description="Fetch comprehensive property details for {address} "
                "Retrieve the following information:\n"
                "- Current price, Number of bedrooms and bathrooms\n"
                "- Square footage, Property type, property taxes\n"
                "- Nearby schools with ratings and distances\n"
                "- Local crime rates and proximity to police stations\n"
                "- Recent sales of similar properties (comparables)\n"
                "- Nearby public transport options\n"
                "- Walkability score\n"
                "- HOA fees\n"
                "- Rental value estimate\n"
                "- Additional relevant information (year built, parking, heating/cooling, etc.)\n\n"
                "Ensure all information is up-to-date and accurate.",
            output_json=PropertyDetails,
            expected_output="A structured JSON object containing property details.",
            agent=real_estate_agent,
            tools=[search_tool, docs_scrape_tool]
        )
        
        # Task to verify property details
        verification_task = Task(
            description=(
                "Verify the real estate details for {address} by reviewing data from both the property information task "
                "and the nearby amenities task.\n"
                "Ensure that the property details such as price, bedrooms, bathrooms, square footage, "
                "lot size, property type, HOA fees, property taxes, school ratings, local crime rates, and recent sales "
                "of comparable properties are accurate.\n"
                "Cross-check nearby amenities (e.g., grocery stores, schools, gyms) and their distances from the property.\n"
                "Confirm public transport options, walkability score, and rental value estimates, ensuring all information is "
                "complete and up-to-date.\n"
                "If any data is missing or incorrect, retrieve the correct data from reliable sources like Zillow, Redfin, "
                "Realtor.com, Walk Score, and government databases."
            ),
            expected_output=(
                "A structured JSON object containing verified property details, including corrected data, "
                "and accurate nearby amenities with their distances from the property."
            ),
            agent=assistant_agent,  # Now responsible for both verifying property info and nearby amenities
            tools=[search_tool, docs_scrape_tool],
        )
        
        # Create the Crew
        real_estate_crew = Crew(
            agents=[real_estate_agent, amenities_finder_agent, assistant_agent],
            tasks=[property_details_task, find_nearby_amenities_task, verification_task],
            verbose=True,
            memory=True
        )
        
        
        result = real_estate_crew.kickoff(inputs={"address": address})
            
        # Print the result
        print(result)
        return jsonify(result)
    else:
        return jsonify({"error": "Property not found for the provided address"}), 404
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

