import { AxiosHeaders } from "axios"
import { client } from "./api"

export const postCreateDebts = (auth: AxiosHeaders | undefined) => {
  return client.post('/debts', { amount: 50000, description: 'name', interest_rate: 0.01, due_date: Date.now() }, { headers: auth })
}