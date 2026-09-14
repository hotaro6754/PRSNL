'use client'

import React, { createContext, useContext, useEffect } from 'react'
import { useStream, type StreamEvent, type StreamStatus } from '@/lib/api'

type Listener = (event: StreamEvent) => void

const listeners = new Set<Listener>()
const subscribe = (listener: Listener) => {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

const StreamStatusContext = createContext<StreamStatus>('connecting')

/** One EventSource for the whole dashboard; pages subscribe to its events. */
export function LiveEventsProvider({ onEvent, children }: { onEvent?: Listener; children: React.ReactNode }) {
  const status = useStream((event) => {
    onEvent?.(event)
    listeners.forEach((l) => l(event))
  })
  return <StreamStatusContext.Provider value={status}>{children}</StreamStatusContext.Provider>
}

export function useStreamStatus(): StreamStatus {
  return useContext(StreamStatusContext)
}

export function useLiveEvents(listener: Listener) {
  useEffect(() => subscribe(listener), [listener])
}
