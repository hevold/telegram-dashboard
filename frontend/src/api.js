import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export const getMapEvents = (source) =>
  api.get("/events/map", { params: source ? { source } : {} }).then((r) => r.data);

export const getEvents = (source, limit = 100) =>
  api.get("/events", { params: { ...(source && { source }), limit } }).then((r) => r.data);

export const createEvent = (data) =>
  api.post("/events", data).then((r) => r.data);

export const updateEventLocation = (id, data) =>
  api.patch(`/events/${id}`, data).then((r) => r.data);

export const deleteEvent = (id) =>
  api.delete(`/events/${id}`);

export const getChannels = () =>
  api.get("/channels").then((r) => r.data);

export const addChannel = (data) =>
  api.post("/channels", data).then((r) => r.data);

export const toggleChannel = (id) =>
  api.patch(`/channels/${id}/toggle`).then((r) => r.data);

export const deleteChannel = (id) =>
  api.delete(`/channels/${id}`);

export const triggerGdelt = () =>
  api.post("/gdelt/fetch").then((r) => r.data);
