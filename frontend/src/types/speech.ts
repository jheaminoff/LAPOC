export type ConversationState = 'idle' | 'listening' | 'thinking' | 'speaking'

export interface VisemeEvent {
  visemeId: number
  audioOffsetMs: number
}

export interface SpeechToken {
  token: string
  region: string
}
