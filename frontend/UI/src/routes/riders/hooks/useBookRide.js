import { useEffect, useState } from "react";
import useAxios from "../../../../api/useAxios.js";
import axios from "axios";

const useBookRide = () => {
    const [loadingState, setLoadingState] = useState(false);
    const api = useAxios();
    const [siteSettings, setSiteSettings] = useState({});
    const [rideDetails, setRideDetails] = useState({
        rideDistance: 0,
        rideDuration: 0,
        ridePrice: 0,
        pickUp_long_lat: null,
        dropOff_long_lat: null,
    });

    const mapboxApiKey = "pk.eyJ1IjoibWFuam90NyIsImEiOiJjbTRna2w4MjIxb2ZqMmpwc2xxdWtkNXRkIn0.Xo8Zm6sEolvzRJbnFlNPQw";
    const mapboxUrlEndpoint = "https://api.mapbox.com";

    const getCoordinates = async (address) => {
        try {
            const response = await axios.get(
                `${mapboxUrlEndpoint}/geocoding/v5/mapbox.places/${encodeURIComponent(
                    address
                )}.json?access_token=${mapboxApiKey}&autocomplete=true`
            );
            if (
                response?.data?.features?.length > 0 &&
                response.data.features[0].center
            ) {
                const [longitude, latitude] = response.data.features[0].center;
                return { latitude, longitude };
            } else {
                console.error("Coordinates not found for the address:", address);
                return null;
            }
        } catch (error) {
            console.error("Error fetching coordinates:", error);
            return null;
        }
    };

    const getSiteSettings = async () => {
        try {
            const response = await api.get("app/site/");
            if (response?.data?.length > 0) {
                setSiteSettings(response.data[0]);
            } else {
                console.error("Site settings not found");
            }
        } catch (err) {
            console.error("Error fetching site settings:", err);
        }
    };

    const startRideBooking = async (pickUpAddress, destinationAddress) => {
        setLoadingState(true);

        try {
            const pickUp = await getCoordinates(pickUpAddress);
            const dropOff = await getCoordinates(destinationAddress);

            if (!pickUp || !dropOff) {
                console.error("Invalid pickup or dropoff coordinates");
                setLoadingState(false);
                return;
            }

            const responseRoute = await axios.get(
                `${mapboxUrlEndpoint}/directions/v5/mapbox/driving/${pickUp.longitude},${pickUp.latitude};${dropOff.longitude},${dropOff.latitude}?access_token=${mapboxApiKey}`
            );

            const rideDuration = responseRoute?.data?.routes?.[0]?.duration / 60 || 0; // Duration in minutes
            const rideDistance = responseRoute?.data?.routes?.[0]?.distance / 1000 || 0; // Distance in kilometers

            // Calculate ride price
            const durationValue = (siteSettings?.price_minute || 0) * rideDuration;
            const distanceValue = (siteSettings?.price_km || 0) * rideDistance;
            const totalPrice =
                Number(siteSettings?.base_price || 0) + durationValue + distanceValue;

            setRideDetails({
                ...rideDetails,
                rideDistance: rideDistance.toFixed(2),
                rideDuration: rideDuration.toFixed(2),
                ridePrice: totalPrice.toFixed(2),
                pickUp_long_lat: `${pickUp.longitude}, ${pickUp.latitude}`,
                dropOff_long_lat: `${dropOff.longitude}, ${dropOff.latitude}`,
            });
        } catch (error) {
            console.error("Error starting ride booking:", error);
        } finally {
            setLoadingState(false);
        }
    };

    useEffect(() => {
        getSiteSettings();
    }, []);

    return {
        getSiteSettings,
        loadingState,
        siteSettings,
        startRideBooking,
        rideDetails,
    };
};

export default useBookRide;
