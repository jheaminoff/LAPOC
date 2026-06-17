export type ConversationState = 'idle' | 'listening' | 'thinking' | 'synthesizing' | 'speaking'

export interface VisemeEvent {
  visemeId: number
  audioOffsetMs: number
}

export interface SpeechToken {
  token: string
  region: string
}
