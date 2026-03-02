import { useState, useEffect, useCallback } from "react";
import DashboardMap from "./components/Map";
import EventFeed from "./components/EventFeed";
import ChannelManager from "./components/ChannelManager";
import AddEventModal from "./components/AddEventModal";
import { getMapEvents, getEvents, triggerGdelt } from "./api";

export default function App() {
  const [mapEvents, setMapEvents] = useState([]);
  const [feedEvents, setFeedEvents] = useState([]);
  const [activeSource, setActiveSource] = useState(null); // null = all
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showChannels, setShowChannels] = useState(false);
  const [gdeltLoading, setGdeltLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadEvents = useCallback(async () => {
    const [map, feed] = await Promise.all([
      getMapEvents(activeSource),
      getEvents(activeSource),
    ]);
    setMapEvents(map);
    setFeedEvents(feed);
    setLastUpdated(new Date());
  }, [activeSource]);

  useEffect(() => {
    loadEvents();
    const interval = setInterval(loadEvents, 60_000); // refresh every minute
    return () => clearInterval(interval);
  }, [loadEvents]);

  const handleGdeltFetch = async () => {
    setGdeltLoading(true);
    await triggerGdelt();
    setTimeout(() => {
      loadEvents();
      setGdeltLoading(false);
    }, 3000);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-800 z-10">
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-white">Telegram Dashboard</span>
          <span className="text-xs text-gray-500">
            {lastUpdated ? `Oppdatert ${lastUpdated.toLocaleTimeString("no")}` : "Laster..."}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Source filter */}
          {["all", "telegram", "gdelt"].map((src) => (
            <button
              key={src}
              onClick={() => setActiveSource(src === "all" ? null : src)}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                (activeSource ?? "all") === src
                  ? src === "telegram"
                    ? "bg-blue-600 text-white"
                    : src === "gdelt"
                    ? "bg-emerald-600 text-white"
                    : "bg-gray-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {src === "all" ? "Alle" : src.charAt(0).toUpperCase() + src.slice(1)}
            </button>
          ))}

          <div className="w-px h-5 bg-gray-700 mx-1" />

          <button
            onClick={handleGdeltFetch}
            disabled={gdeltLoading}
            className="px-3 py-1 rounded text-xs font-medium bg-emerald-800 hover:bg-emerald-700 disabled:opacity-50 transition-colors"
          >
            {gdeltLoading ? "Henter GDELT..." : "Hent GDELT"}
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-3 py-1 rounded text-xs font-medium bg-blue-700 hover:bg-blue-600 transition-colors"
          >
            + Legg til hendelse
          </button>

          <button
            onClick={() => setShowChannels(true)}
            className="px-3 py-1 rounded text-xs font-medium bg-gray-700 hover:bg-gray-600 transition-colors"
          >
            Kanaler
          </button>
        </div>
      </header>

      {/* Main layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Map */}
        <div className="flex-1">
          <DashboardMap
            events={mapEvents}
            selectedEvent={selectedEvent}
            onSelectEvent={setSelectedEvent}
          />
        </div>

        {/* Event feed sidebar */}
        <div className="w-80 bg-gray-900 border-l border-gray-800 overflow-y-auto">
          <EventFeed
            events={feedEvents}
            selectedEvent={selectedEvent}
            onSelectEvent={setSelectedEvent}
            onRefresh={loadEvents}
          />
        </div>
      </div>

      {/* Modals */}
      {showAddModal && (
        <AddEventModal
          onClose={() => setShowAddModal(false)}
          onSaved={() => { setShowAddModal(false); loadEvents(); }}
        />
      )}
      {showChannels && (
        <ChannelManager onClose={() => setShowChannels(false)} />
      )}
    </div>
  );
}
