import { useEffect, useState } from 'react';
import Map, { Marker } from 'react-map-gl';

const MapComp = ({ rideObj }) => {
    const [rideCoordinates, setRideCoordinates] = useState({
        pickupLong: -73.977785, // Default longitude
        pickupLat: 40.63258,   // Default latitude
        dropOffLong: -73.977785, // Default longitude
        dropOffLat: 40.63258,   // Default latitude
    });

    useEffect(() => {
        if (rideObj) {
            const dropOffLangLat = rideObj?.drop_off_long_lat;
            const pickUpLangLat = rideObj?.pickup_long_lat;

            const pickUp = pickUpLangLat?.split(",");
            const dropOff = dropOffLangLat?.split(",");

            if (pickUp?.length === 2 && dropOff?.length === 2) {
                setRideCoordinates({
                    pickupLong: Number(pickUp[0]) || -73.977785,
                    pickupLat: Number(pickUp[1]) || 40.63258,
                    dropOffLong: Number(dropOff[0]) || -73.977785,
                    dropOffLat: Number(dropOff[1]) || 40.63258,
                });
            }
        }
    }, [rideObj]);

    return (
        <Map
            mapboxAccessToken="pk.eyJ1IjoibWFuam90NyIsImEiOiJjbTRna2w4MjIxb2ZqMmpwc2xxdWtkNXRkIn0.Xo8Zm6sEolvzRJbnFlNPQw"
            initialViewState={{
                longitude: rideCoordinates.pickupLong,
                latitude: rideCoordinates.pickupLat,
                zoom: 8.5,
            }}
            style={{ width: "100%", minHeight: "40rem" }}
            mapStyle="mapbox://styles/mapbox/streets-v12"
        >
            {rideObj?.ride_status !== "In Progress" && (
                <Marker
                    longitude={rideCoordinates.pickupLong}
                    latitude={rideCoordinates.pickupLat}
                    anchor="bottom"
                >
                    <div className="w-[25px] h-[25px] rounded-full bg-blue-900" />
                </Marker>
            )}

            <Marker
                longitude={rideCoordinates.dropOffLong}
                latitude={rideCoordinates.dropOffLat}
                anchor="bottom"
            >
                <div className="w-[25px] h-[25px] rounded-full bg-red-900" />
            </Marker>
        </Map>
    );
};

export default MapComp;
