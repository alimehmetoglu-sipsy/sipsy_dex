export default function LoginLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Login sayfası için sidebar yok, sadece children'ı render et
  return <>{children}</>
}