import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Hotel } from '../types';

interface HotelContextType {
  hotels: Hotel[];
  selectedHotel: Hotel | null;
  setSelectedHotel: (hotel: Hotel) => void;
  selectHotelById: (hotelId: number) => void;
  loadingHotels: boolean;
  refreshHotels: () => Promise<void>;
}

const HotelContext = createContext<HotelContextType | undefined>(undefined);

export const HotelProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [selectedHotel, setSelectedHotelState] = useState<Hotel | null>(null);
  const [loadingHotels, setLoadingHotels] = useState(true);

  const fetchHotels = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoadingHotels(false);
      return;
    }
    try {
      setLoadingHotels(true);
      const data = await apiService.getHotels();
      if (Array.isArray(data)) {
        setHotels(data);
        if (data.length > 0) {
          const savedHotelId = localStorage.getItem('selected_hotel_id');
          let initialHotel = data[0];

          if (savedHotelId) {
            const found = data.find((h: Hotel) => h.hotel_id === Number(savedHotelId));
            if (found) initialHotel = found;
          }

          setSelectedHotelState(initialHotel);
          localStorage.setItem('selected_hotel_id', initialHotel.hotel_id.toString());
        }
      }
    } catch (err) {
      console.error('Failed to load hotels list in HotelContext:', err);
    } finally {
      setLoadingHotels(false);
    }
  };

  useEffect(() => {
    fetchHotels();
  }, []);

  const setSelectedHotel = (hotel: Hotel) => {
    setSelectedHotelState(hotel);
    localStorage.setItem('selected_hotel_id', hotel.hotel_id.toString());
  };

  const selectHotelById = (hotelId: number) => {
    const found = hotels.find((h) => h.hotel_id === hotelId);
    if (found) {
      setSelectedHotel(found);
    }
  };

  return (
    <HotelContext.Provider
      value={{
        hotels,
        selectedHotel,
        setSelectedHotel,
        selectHotelById,
        loadingHotels,
        refreshHotels: fetchHotels,
      }}
    >
      {children}
    </HotelContext.Provider>
  );
};

export const useHotel = (): HotelContextType => {
  const context = useContext(HotelContext);
  if (!context) {
    throw new Error('useHotel must be used within a HotelProvider');
  }
  return context;
};
