import axios, { AxiosError } from "axios";

export const createAxiosClient = () => {
  const client = axios.create({
    baseURL: "http://localhost:8080",
    headers: {
      "Content-Type": "application/json"
    },
    withCredentials: true
  });

  client.interceptors.request.use(
    (config) => {
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response?.status === 401) {
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const client = createAxiosClient();
