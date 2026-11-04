// Today in Spain, the Actor's default asOfDate. The prerendered HTML carries the build date (kept in
// the payload so hydration matches); the browser replaces it with the visitor's today after mount.
export function useEditionDate(locale: string) {
  const now = useState("edition-now", () => Date.now())
  onMounted(() => {
    now.value = Date.now()
  })
  const long = computed(() =>
    new Intl.DateTimeFormat(locale, {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "Europe/Madrid",
    }).format(now.value),
  )
  const short = computed(() =>
    new Intl.DateTimeFormat(locale, { day: "2-digit", month: "short", year: "numeric", timeZone: "Europe/Madrid" })
      .format(now.value)
      .replace(".", ""),
  )
  const iso = computed(() => new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Madrid" }).format(now.value))
  return { long, short, iso }
}
