import axios from 'axios'

const creatorApiClient = axios.create({
  baseURL: import.meta.env.VITE_CREATOR_API_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface AbilityRequest {
  abilityDescription: string
  cardDescription: string
}

export interface AbilityResponse {
  triggerDefinition: any
  targetDefinition: any[]
  effect: string
  amount: any
}

export const creatorApi = {
  parseAbility: async (request: AbilityRequest): Promise<AbilityResponse> => {
    const response = await creatorApiClient.post('/parse-ability', request)
    return response.data
  },
}

export default creatorApi
