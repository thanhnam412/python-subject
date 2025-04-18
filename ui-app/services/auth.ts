import { AxiosHeaders } from "axios"
import { client } from "./api"

export const postLogin = (params: { username: string, password: string }) => {
  return client.post('/api/login', params, { withCredentials: false, baseURL: 'http://localhost:3000' })
}

export const postLogout = (auth: AxiosHeaders | undefined) => {
  return client.post('/auth/logout', {}, { headers: auth })
}
