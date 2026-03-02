import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import { format } from "date-fns";
import { nb } from "date-fns/locale";

// Auto-pan to selected event
function FlyToEvent({ event }) {
  const map = useMap();
  useEffect(() => {
    if (event?.latitude && event?.longitude) {
      map.flyTo([event.latitude, event.longitude], 7, { duration: 1 });
    }
  }, [event, map]);
  return null;
}

const SOURCE_COLORS = {
  telegram: "#3b82f6",  // blue
  gdelt: "#10b981",     // emerald
};

export default function DashboardMap({ events, selectedEvent, onSelectEvent }) {
  return (
    <MapContainer
      center={[30, 20]}
      zoom={3}
      style={{ height: "100%", width: "100%" }}
      className="z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {selectedEvent && <FlyToEvent event={selectedEvent} />}

      {events.map((ev) => (
        <CircleMarker
          key={ev.id}
          center={[ev.latitude, ev.longitude]}
          radius={selectedEvent?.id === ev.id ? 10 : 7}
          pathOptions={{
            color: SOURCE_COLORS[ev.source] ?? "#9ca3af",
            fillColor: SOURCE_COLORS[ev.source] ?? "#9ca3af",
            fillOpacity: 0.8,
            weight: selectedEvent?.id === ev.id ? 3 : 1,
          }}
          eventHandlers={{ click: () => onSelectEvent(ev) }}
        >
          <Popup className="dark-popup">
            <div className="text-sm max-w-xs">
              <div className="flex items-center gap-2 mb-1">
                <span
                  className="px-1.5 py-0.5 rounded text-xs font-bold text-white"
                  style={{ background: SOURCE_COLORS[ev.source] }}
                >
                  {ev.source.toUpperCase()}
                </span>
                {ev.channel_name && (
                  <span className="text-gray-500 text-xs">@{ev.channel_name}</span>
                )}
              </div>
              <p className="font-medium mb-1 leading-snug">
                {ev.title?.slice(0, 120) || "Ingen tittel"}
              </p>
              {ev.location_name && (
                <p className="text-gray-500 text-xs mb-1">📍 {ev.location_name}</p>
              )}
              <p className="text-gray-400 text-xs">
                {ev.event_date
                  ? format(new Date(ev.event_date), "d. MMM yyyy HH:mm", { locale: nb })
                  : ""}
              </p>
              {ev.url && (
                <a
                  href={ev.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-400 text-xs underline mt-1 block"
                >
                  Åpne kilde →
                </a>
              )}
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
