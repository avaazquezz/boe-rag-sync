import gsap from "gsap"
import { CustomEase } from "gsap/CustomEase"
import { ScrollTrigger } from "gsap/ScrollTrigger"
import { MOTION } from "~/utils/motion"

// Native scroll, no smoothing library: ScrollTrigger reads the real scroll position.
export default defineNuxtPlugin(() => {
  gsap.registerPlugin(ScrollTrigger, CustomEase)
  CustomEase.create("brand", "0.625,0.05,0,1") // moves and transitions
  CustomEase.create("brand-out", "0.16,1,0.3,1") // entrances
  gsap.defaults({ ease: "brand", duration: MOTION.dur.reveal })
  ScrollTrigger.config({ ignoreMobileResize: true })
  void document.fonts.ready.then(() => ScrollTrigger.refresh())
})
