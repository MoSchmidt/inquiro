import ax from 'axios';

const axios = ax.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// optional: attach tokens globally later
// axios.interceptors.request.use((config) => {
//   const token = useAuthStore().accessToken
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

export default axios;
