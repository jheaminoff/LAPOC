import { Suspense, useRef, Component, type ReactNode, type ErrorInfo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { useGLTF, ContactShadows, Environment } from '@react-three/drei'
import * as THREE from 'three'
import modelUrl from '@/assets/ram.glb'
import type { ConversationState } from '@/types/speech'
import styles from './ChatMascot.module.css'

interface ChatMascotProps {
  visemeId: number
  state: ConversationState
}

function GlbModel({ visemeId, state }: ChatMascotProps) {
  const group = useRef<THREE.Group>(null)
  const jawBoneRef = useRef<THREE.Bone | null>(null)
  const { scene } = useGLTF(modelUrl)
  const foundBones = useRef(false)

  if (!foundBones.current) {
    scene.traverse((obj) => {
      if (obj instanceof THREE.Bone && !jawBoneRef.current) {
        const n = obj.name.toLowerCase()
        if (n.includes('jaw') || n.includes('beak') || n.includes('mouth') || n.includes('chin') || n.includes('mandible')) {
          jawBoneRef.current = obj
        }
      }
    })
    foundBones.current = true
  }

  useFrame((_, delta) => {
    if (!group.current) return
    const t = performance.now() / 1000

    switch (state) {
      case 'idle':
        group.current.rotation.y += delta * 0.15
        break
      case 'listening':
        group.current.rotation.y += delta * 0.08
        group.current.position.y = Math.sin(t * 1.5) * 0.03
        break
      case 'thinking':
        group.current.rotation.y += delta * 0.04
        group.current.position.y = Math.sin(t * 1.0) * 0.04
        break
      case 'speaking':
        group.current.position.y = Math.sin(t * 2.0) * 0.02
        break
    }

    const jaw = jawBoneRef.current
    if (jaw) {
      const target = visemeId !== 0 ? 0.25 : 0
      jaw.rotation.x = THREE.MathUtils.lerp(jaw.rotation.x, target, delta * 10)
    }
  })

  return (
    <group ref={group} dispose={null}>
      <primitive object={scene} scale={0.7} />
    </group>
  )
}

interface EBState { hasError: boolean }
class GlbErrorBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, EBState> {
  state: EBState = { hasError: false }
  static getDerivedStateFromError(): EBState { return { hasError: true } }
  componentDidCatch(err: Error, info: ErrorInfo) {
    console.warn('[ChatMascot] GLB load failed, using procedural fallback:', err, info)
  }
  render() { return this.state.hasError ? this.props.fallback : this.props.children }
}

function ProceduralMascot(_props: ChatMascotProps) {
  const group = useRef<THREE.Group>(null)
  const t = useRef(0)

  useFrame((_s, delta) => {
    t.current += delta
    if (!group.current) return
    group.current.position.y = Math.sin(t.current * 1.5) * 0.04
    group.current.rotation.y += delta * 0.15
  })

  const white = new THREE.MeshStandardMaterial({ color: '#d0d5e8' })
  const dark = new THREE.MeshStandardMaterial({ color: '#1c2253' })

  return (
    <group ref={group}>
      <mesh material={white}><sphereGeometry args={[0.5, 20, 14]} /></mesh>
      <mesh position={[0, 0.4, 0.3]} material={white}><sphereGeometry args={[0.3, 16, 12]} /></mesh>
      <mesh position={[0.12, 0.45, 0.5]} material={dark}><sphereGeometry args={[0.04, 8, 8]} /></mesh>
      <mesh position={[-0.12, 0.45, 0.5]} material={dark}><sphereGeometry args={[0.04, 8, 8]} /></mesh>
      <mesh position={[0, 0.38, 0.58]} material={new THREE.MeshStandardMaterial({ color: '#c8a84e' })}>
        <boxGeometry args={[0.08, 0.04, 0.15]} />
      </mesh>
    </group>
  )
}

export default function ChatMascot(props: ChatMascotProps) {
  return (
    <div className={styles.container}>
      <Canvas shadows camera={{ position: [0, 1.2, 3.5], fov: 40 }}>
        <ambientLight intensity={0.6} />
        <spotLight position={[4, 4, 4]} angle={0.3} penumbra={0.8} intensity={0.8} />
        <directionalLight position={[-3, 3, -3]} intensity={0.4} />
        <GlbErrorBoundary fallback={<ProceduralMascot {...props} />}>
          <Suspense fallback={<ProceduralMascot {...props} />}>
            <GlbModel {...props} />
          </Suspense>
        </GlbErrorBoundary>
        <ContactShadows position={[0, -0.6, 0]} opacity={0.35} width={3} height={3} blur={2} />
        <Environment preset="city" />
      </Canvas>
    </div>
  )
}
