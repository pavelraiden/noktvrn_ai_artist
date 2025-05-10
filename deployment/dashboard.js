document.addEventListener("DOMContentLoaded", () => {
    const artistListDiv = document.getElementById("artist-list");
    const artistCardTemplate = document.getElementById("artist-card-template");

    // Function to fetch artists and render them
    async function fetchAndRenderArtists() {
        try {
            const response = await fetch("/api/artists"); // Assumes Flask serves this endpoint
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const artists = await response.json();

            artistListDiv.innerHTML = ""; // Clear loading message

            if (artists.length === 0) {
                artistListDiv.innerHTML = "<p>No artists found.</p>";
                return;
            }

            artists.forEach(artist => {
                const cardClone = artistCardTemplate.content.cloneNode(true);
                const cardElement = cardClone.querySelector(".artist-card");

                cardElement.dataset.artistId = artist.id;
                cardElement.querySelector("h3").textContent = artist.name || "Unnamed Artist";
                cardElement.querySelector(".status").textContent = artist.status || "Unknown";
                // Populate other stats if available in the API response
                // cardElement.querySelector(".cycles").textContent = artist.cycles_completed || 0;
                // cardElement.querySelector(".last-active").textContent = artist.last_active || "N/A";
                // cardElement.querySelector(".summary-text").textContent = artist.recent_output_summary || "No recent output available.";

                // Add event listeners for buttons
                const startButton = cardElement.querySelector(".start-button");
                const pauseButton = cardElement.querySelector(".pause-button");

                startButton.addEventListener("click", () => updateArtistStatus(artist.id, "running"));
                pauseButton.addEventListener("click", () => updateArtistStatus(artist.id, "paused"));

                artistListDiv.appendChild(cardClone);
            });

        } catch (error) {
            console.error("Error fetching artists:", error);
            artistListDiv.innerHTML = "<p>Error loading artists. Please check the console.</p>";
        }
    }

    // Function to update artist status via API
    async function updateArtistStatus(artistId, newStatus) {
        try {
            const response = await fetch(`/api/artists/${artistId}/status`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ status: newStatus }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`API error: ${errorData.message || response.statusText}`);
            }

            const updatedArtist = await response.json();

            // Update the status on the specific artist card
            const cardElement = artistListDiv.querySelector(`.artist-card[data-artist-id="${artistId}"]`);
            if (cardElement) {
                cardElement.querySelector(".status").textContent = updatedArtist.status;
            }

            console.log(`Artist ${artistId} status updated to ${updatedArtist.status}`);
            // Optionally show a success message to the user

        } catch (error) {
            console.error(`Error updating artist ${artistId} status:`, error);
            // Optionally show an error message to the user
            alert(`Failed to update artist status: ${error.message}`);
        }
    }

    // Initial fetch and render
    fetchAndRenderArtists();
});

