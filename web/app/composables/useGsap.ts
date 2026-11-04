import gsap from "gsap"
import type { Ref } from "vue"

export type MotionConditions = { motion: boolean; reduce: boolean; desktop: boolean; finePointer: boolean }
type Setup = (c: MotionConditions, ctx: gsap.Context) => void | (() => void)

// Every animation lives inside a matchMedia context scoped to the component: it is reverted on
// unmount and rebuilt when the visitor's reduced-motion or viewport conditions change.
export function useGsap(scope: Ref<HTMLElement | null>, setup: Setup) {
  let mm: gsap.MatchMedia | undefined
  onMounted(() => {
    mm = gsap.matchMedia()
    mm.add(
      {
        motion: "(prefers-reduced-motion: no-preference)",
        reduce: "(prefers-reduced-motion: reduce)",
        desktop: "(min-width: 1024px)",
        finePointer: "(hover: hover) and (pointer: fine)",
      },
      (ctx) => setup(ctx.conditions as MotionConditions, ctx),
      scope.value ?? undefined,
    )
  })
  onUnmounted(() => mm?.revert())
}
