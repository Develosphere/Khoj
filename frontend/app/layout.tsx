import "../globals.css";
import type { ReactNode } from "react";
import ApplicationShell from "../components/shared/application-shell";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body><ApplicationShell>{children}</ApplicationShell></body>
    </html>
  );
}
