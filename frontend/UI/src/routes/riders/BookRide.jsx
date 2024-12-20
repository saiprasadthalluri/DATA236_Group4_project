import sedanSVG from "../../assets/svgs/sedan-11.svg";
import suvSVG from "../../assets/svgs/suv.svg";
import luxuryCar from "../../assets/svgs/luxury.svg";
import { useEffect, useRef, useState } from "react";
import useBookRide from "./hooks/useBookRide";
import useGetContext from "../../../context/useGetContext";
import useAxios from "../../../api/useAxios";
import { useNavigate } from "react-router-dom";
import { AddressAutofill } from "@mapbox/search-js-react";

const BookRide = () => {
    const { startRideBooking, rideDetails, loadingState, siteSettings } = useBookRide();
    const [pickUpAddress, setPickupAddress] = useState("");
    const [dropOffAddress, setDropOffAddress] = useState("");
    const { userDecodedToken, setErrorAPI, setSuccessMsgAPI } = useGetContext();
    const [carType, setCarType] = useState("");
    const api = useAxios();
    const navigate = useNavigate();
    const timeoutRef = useRef(null);

    // Hardcoded Mapbox API Key
    const MAPBOX_API_KEY = "pk.eyJ1IjoibWFuam90NyIsImEiOiJjbTRna2w4MjIxb2ZqMmpwc2xxdWtkNXRkIn0.Xo8Zm6sEolvzRJbnFlNPQw";

    const handleButtonClick = async (e) => {
        e.preventDefault();
        if (rideDetails?.rideDuration && rideDetails?.rideDistance && carType) {
            const data = {
                rider_id: userDecodedToken?.riderProfileID,
                pick_up_location: pickUpAddress,
                drop_off_location: dropOffAddress,
                pickup_long_lat: rideDetails.pickUp_long_lat,
                drop_off_long_lat: rideDetails.dropOff_long_lat,
                distance: rideDetails?.rideDistance,
                ride_duration: rideDetails?.rideDuration,
                ride_car_type: carType,
            };
            try {
                await api.post("rides/book/", data);
                setSuccessMsgAPI("Your ride has been successfully booked");
                navigate("/rider/bookings");
            } catch (err) {
                if (err?.response?.status === 400 && err?.response?.data?.Error) {
                    setErrorAPI(err?.response?.data?.Error);
                } else if (err?.response?.status === 500) {
                    setErrorAPI("Server Error, Team has been notified");
                } else {
                    setErrorAPI("Oops! Something went wrong.");
                }
            }
        } else {
            setErrorAPI("Please complete all fields.");
        }
    };

    const handleDropOffAdd = (e) => {
        setDropOffAddress(e.target.value);
        if (pickUpAddress && e.target.value) {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
            timeoutRef.current = setTimeout(() => {
                startRideBooking(pickUpAddress, e.target.value);
            }, 1000);
        }
    };

    useEffect(() => {
        // Cleanup the timeout on component unmount
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, []);

    return (
        <div className="w-full h-full pt-12">
            <div className="w-[95%] mx-auto">
                <form className="flex border-2 flex-col gap-3 w-[90%] lg:w-[60%] mx-auto mt-12 md:mt-2 mb-2 shadow-lg p-4 rounded-sm">
                    <h2 className="text-center text-xl font-semibold">Book your ride</h2>
                    <p className="text-center text-slate-500 hover:text-blue-600">
                        A few seconds to book your ride
                    </p>

                    <div className="form-row">
                        <label htmlFor="pickupAddress">Pick up Address</label>
                        <AddressAutofill accessToken={MAPBOX_API_KEY}>
                            <input
                                type="text"
                                value={pickUpAddress}
                                autoComplete="street-address"
                                onChange={(e) => setPickupAddress(e.target.value)}
                                placeholder="Pick-up address"
                                className="w-full py-3 rounded-sm px-1 border-2 text-md mb-2 mt-3"
                            />
                        </AddressAutofill>
                    </div>

                    <div className="form-row">
                        <label htmlFor="dropOff">Drop off Address</label>
                        <AddressAutofill accessToken={MAPBOX_API_KEY}>
                            <input
                                type="text"
                                disabled={!pickUpAddress}
                                value={dropOffAddress}
                                onChange={handleDropOffAdd}
                                id="dropOff"
                                placeholder="Drop-off address"
                                autoComplete="street-address"
                                className="w-full py-3 rounded-sm px-1 border-2 text-md mt-3"
                            />
                        </AddressAutofill>
                    </div>

                    <div className="form-row">
                        <label htmlFor="">Car type</label>
                        <div className="flex gap-4 justify-center mb-3 mt-3 w-full">
                            {[{
                                id: "sedanCar", type: "Sedan", icon: sedanSVG
                            }, {
                                id: "suvCar", type: "SUV", icon: suvSVG
                            }, {
                                id: "luxuryCar", type: "Luxury", icon: luxuryCar
                            }].map(({ id, type, icon }) => (
                                <label htmlFor={id} className="cursor-pointer w-full" key={id}>
                                    <div className="flex flex-col relative hover:shadow-2xl border-2 hover:shadow-deep-purple/50 py-2 rounded-md">
                                        <input
                                            type="radio"
                                            onChange={() => setCarType(type)}
                                            name="carCategory"
                                            id={id}
                                            className="absolute left-2 top-2"
                                        />
                                        <img src={icon} alt={type} className="w-[48px] mx-auto h-[48px]" />
                                        <span className="mt-auto text-center">{type}</span>
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>

                    <div className="form-row">
                        <label htmlFor="paymentMethod">Payment method</label>
                        <select
                            name="paymentMethod"
                            id="paymentMethod"
                            className="w-full py-3 rounded-sm px-1 border-2 text-md mt-3"
                        >
                            <option value="Cash">Cash</option>
                            <option value="Card">Card</option>
                            <option value="Wallet">Wallet</option>
                        </select>
                    </div>

                    <div className="mt-4">
                        <ul className="flex justify-around items-center">
                            <li className="text-xs sm:text-base md:text-base">
                                Distance: {`${!loadingState ? `${rideDetails?.rideDistance || 0} KM` : "Loading..."}`}
                            </li>
                            <li className="text-xs sm:text-base md:text-base font-semibold text-green-800">
                                Price: {`${!loadingState ? `$${rideDetails?.ridePrice || 0}` : "Loading..."}`}
                            </li>
                            <li className="text-xs sm:text-base md:text-base">
                                Duration: {`${!loadingState ? `${rideDetails?.rideDuration || 0} minutes` : "Loading..."}`}
                            </li>
                        </ul>
                    </div>

                    <div className="mt-4 flex items-center gap-2">
                        <h6>Pricing Policy:</h6>
                        <ul className="flex gap-4 items-center">
                            <li className="text-slate-500 text-xs">
                                Base price: {siteSettings?.base_price || 0} $
                            </li>
                            <li className="text-slate-500 text-xs">
                                Price per km: {siteSettings?.price_km || 0} $
                            </li>
                            <li className="text-slate-500 text-xs">
                                Price per minute: {siteSettings?.price_minute || 0} $
                            </li>
                        </ul>
                    </div>

                    <button
                        onClick={handleButtonClick}
                        className={`w-full bg-deep-purple py-3 mt-4 rounded-sm text-white text-md ${
                            !pickUpAddress || !dropOffAddress || !carType ? "opacity-50 cursor-not-allowed" : ""
                        }`}
                        disabled={!pickUpAddress || !dropOffAddress || !carType}
                    >
                        Book now {">"}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default BookRide;
