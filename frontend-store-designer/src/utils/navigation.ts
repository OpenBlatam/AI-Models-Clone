import { useRouter } from 'next/navigation'

export function useNavigation() {
  const router = useRouter()

  return {
    goTo: (path: string) => router.push(path),
    replace: (path: string) => router.replace(path),
    back: () => router.back(),
    refresh: () => router.refresh(),
  }
}


