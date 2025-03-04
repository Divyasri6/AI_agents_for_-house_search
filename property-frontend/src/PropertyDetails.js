import React, { useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";

const PropertyDetails = () => {
  const [address, setAddress] = useState("");
  const [property, setProperty] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchPropertyDetails = async () => {
    if (!address) {
      setError("Please enter an address.");
      setProperty(null);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.get("http://127.0.0.1:5000/api/property", {
        params: { address },
      });
      console.log("Raw API Response:", response.data);
      const data = typeof response.data === "string" ? JSON.parse(response.data) : response.data;
      console.log("Parsed API Response:", data); // 👈 Log parsed data

      if (!data["Property Details"]) {
        console.log("Error: Property Details key missing"); // 👈 Debug log
        setError("Property details not found.");
        setProperty(null);
      } else {
        setProperty(data);
      }
    } catch (err) {
      console.error("API Fetch Error:", err);
      setError("Error fetching property details.");
      setProperty(null);
    }

    setLoading(false);
  };

  return (
    <div className="container my-4">
      <h1 className="text-center mb-4">Property Details</h1>

      <input
        type="text"
        className="form-control mb-3"
        placeholder="Enter address"
        value={address}
        onChange={(e) => setAddress(e.target.value)}
      />
      <button className="btn btn-primary" onClick={fetchPropertyDetails}>Search</button>

      {error && <p className="text-danger mt-3">{error}</p>}
      {loading && <p>Loading...</p>}

      {property && !loading && (
        <>
          <div className="card mb-4">
            <div className="card-body">
              <h3 className="card-title">{property["Property Details"].Address}</h3>
              <p><strong>Price:</strong> {property["Property Details"].Price}</p>
              <p><strong>Bedrooms:</strong> {property["Property Details"].Bedrooms}</p>
              <p><strong>Bathrooms:</strong> {property["Property Details"].Bathrooms}</p>
              <p><strong>Square Footage:</strong> {property["Property Details"]["Square Footage"]}</p>
              <p><strong>Lot Size:</strong> {property["Property Details"]["Lot Size"]}</p>
              <p><strong>Property Type:</strong> {property["Property Details"]["Property Type"]}</p>
              <p><strong>HOA Fees:</strong> {property["Property Details"]["HOA Fees"]}</p>
              <p><strong>Property Taxes:</strong> {property["Property Details"]["Property Taxes"]}</p>
              <p><strong>Local Crime Rates:</strong> {property["Property Details"]["Local Crime Rates"]}</p>
              {/* School Ratings */}
              <h4>School Ratings</h4>
              <p><strong>Elementary School:</strong> {property["Property Details"]["School Ratings"]["Elementary School"]}</p>
              <p><strong>Middle School:</strong> {property["Property Details"]["School Ratings"]["Middle School"]}</p>
              <p><strong>High School:</strong> {property["Property Details"]["School Ratings"]["High School"]}</p>
          
              {/* Recent Sales of Comparable Properties */}
              {property["Property Details"]["Recent Sales of Comparable Properties"] &&
                  Array.isArray(property["Property Details"]["Recent Sales of Comparable Properties"]) &&
                  property["Property Details"]["Recent Sales of Comparable Properties"].length > 0 ? (
                    <div className="mt-4">
                      <h4>Recent Sales of Comparable Properties</h4>
                      <ul className="list-group">
                        {property["Property Details"]["Recent Sales of Comparable Properties"].map((comp, index) => (
                          <li key={index} className="list-group-item">
                            <strong>{comp.Address}</strong> - {comp.Price}
                          </li>
                        ))}
                      </ul>
                </div>
            ) : (
              <p className="text-muted">No recent sales data available.</p>
            )}
              
            </div>
          </div>

          <div className="mt-4">
            <h2>Nearby Amenities</h2>
            {["Grocery Stores", "Hospitals", "Pharmacies", "Gyms", "Restaurants"].map((category) => (
              <div key={category} className="mb-4">
                <h4>{category}</h4>
                <ul className="list-group">
                  {property["Nearby Amenities"][category].map((item, index) => (
                    <li key={index} className="list-group-item">
                      <strong>{item.Name}</strong>: {item.Distance}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default PropertyDetails;
