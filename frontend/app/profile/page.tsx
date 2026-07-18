"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function ProfilePage() {
  const router = useRouter();
  const supabase = createClient();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function loadUser() {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push("/login");
      } else {
        setEmail(user.email || "");
      }
    }
    loadUser();
  }, [router, supabase.auth]);

  async function handleUpdateProfile(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    setIsLoading(true);

    try {
      const updates: { email?: string; password?: string } = {};
      if (email) updates.email = email;
      if (password) updates.password = password;

      if (Object.keys(updates).length === 0) {
        setMessage({ type: "error", text: "Değiştirilecek veri bulunamadı." });
        return;
      }

      const { error } = await supabase.auth.updateUser(updates);

      if (error) {
        throw error;
      }

      setMessage({ type: "success", text: "Profil bilgileriniz başarıyla güncellendi." });
      setPassword(""); // Clear password field after update
    } catch (err) {
      setMessage({
        type: "error",
        text: err instanceof Error ? err.message : "Güncelleme sırasında hata oluştu.",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-muted/30">
      <header className="border-b bg-background">
        <div className="mx-auto max-w-5xl px-6 py-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/dashboard">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Dashboard
            </Link>
          </Button>
        </div>
      </header>

      <div className="mx-auto max-w-2xl space-y-6 px-6 py-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Profil Ayarları</h1>
          <p className="mt-2 text-muted-foreground">
            E-posta ve şifre bilgilerinizi buradan güncelleyebilirsiniz.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Hesap Bilgileri</CardTitle>
            <CardDescription>
              Bilgilerinizi değiştirmek için aşağıdaki formu kullanın.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">E-posta</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="ornek@email.com"
                />
                <p className="text-xs text-muted-foreground">
                  E-posta değişikliği doğrulama gerektirebilir.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Yeni Şifre</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Sadece değiştirmek istiyorsanız girin"
                />
              </div>

              {message && (
                <Alert variant={message.type === "error" ? "destructive" : "default"} className={message.type === "success" ? "border-green-500 text-green-700" : ""}>
                  <AlertDescription>{message.text}</AlertDescription>
                </Alert>
              )}

              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Güncelleniyor..." : "Değişiklikleri Kaydet"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
