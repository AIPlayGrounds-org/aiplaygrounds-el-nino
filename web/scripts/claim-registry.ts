import { parse } from 'smol-toml'

export type RegistryClaim = {
  id: string
  claimEs: string
  status: string
}

type RegistryDocument = {
  claim?: unknown
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

export const parseClaims = (registryText: string): RegistryClaim[] => {
  const document = parse(registryText) as RegistryDocument
  if (!Array.isArray(document.claim)) {
    throw new Error('claims registry has no [[claim]] entries')
  }

  return document.claim.map((value, index) => {
    if (!isRecord(value)) throw new Error(`claim ${index + 1} is not a table`)
    const id = value.id
    const claimEs = value.claim_es
    const status = value.status
    if (typeof id !== 'string' || typeof claimEs !== 'string' || typeof status !== 'string') {
      throw new Error(`claim ${index + 1} must define id, claim_es and status`)
    }
    return { id, claimEs, status }
  })
}
