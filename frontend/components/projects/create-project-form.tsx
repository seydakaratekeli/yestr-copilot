"use client";

import { useActionState } from "react";
import Link from "next/link";

import {
  createProject,
  type ProjectActionState,
} from "@/app/projects/actions";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

import { CreateProjectSubmit } from "./create-project-submit";

const initialState: ProjectActionState = {
  success: false,
  message: null,
};

function FieldError({
  errors,
}: {
  errors?: string[];
}) {
  if (!errors?.length) {
    return null;
  }

  return (
    <p className="text-sm text-destructive">
      {errors[0]}
    </p>
  );
}

export function CreateProjectForm() {
  const [state, formAction] = useActionState(
    createProject,
    initialState,
  );

  return (
    <form action={formAction} className="space-y-6">
      {state.message && !state.success && (
        <Alert variant="destructive">
          <AlertDescription>
            {state.message}
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Temel bilgiler</CardTitle>
          <CardDescription>
            Projenin kimlik ve konum bilgilerini girin.
          </CardDescription>
        </CardHeader>

        <CardContent className="grid gap-5 md:grid-cols-2">
          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="name">Proje adı *</Label>
            <Input
              id="name"
              name="name"
              placeholder="Örneğin: Ankara Kamu Hizmet Binası"
              required
            />

            <FieldError
              errors={state.fieldErrors?.name}
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="description">
              Proje açıklaması
            </Label>

            <Textarea
              id="description"
              name="description"
              rows={4}
              placeholder="Projenin kapsamını kısaca açıklayın."
            />

            <FieldError
              errors={state.fieldErrors?.description}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="city">Şehir</Label>

            <Input
              id="city"
              name="city"
              placeholder="Ankara"
            />

            <FieldError errors={state.fieldErrors?.city} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="district">İlçe</Label>

            <Input
              id="district"
              name="district"
              placeholder="Çankaya"
            />

            <FieldError
              errors={state.fieldErrors?.district}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Bina bilgileri</CardTitle>
          <CardDescription>
            Analizlerde kullanılacak temel yapı verilerini
            girin.
          </CardDescription>
        </CardHeader>

        <CardContent className="grid gap-5 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="projectType">
              Proje türü *
            </Label>

            <Select
              name="projectType"
              defaultValue="new_building"
            >
              <SelectTrigger id="projectType">
                <SelectValue placeholder="Proje türü seçin" />
              </SelectTrigger>

              <SelectContent>
                <SelectItem value="new_building">
                  Yeni bina
                </SelectItem>

                <SelectItem value="existing_building">
                  Mevcut bina / renovasyon
                </SelectItem>
              </SelectContent>
            </Select>

            <FieldError
              errors={state.fieldErrors?.projectType}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="buildingType">
              Bina kullanım türü
            </Label>

            <Select name="buildingType">
              <SelectTrigger id="buildingType">
                <SelectValue placeholder="Bina türü seçin" />
              </SelectTrigger>

              <SelectContent>
                <SelectItem value="public">
                  Kamu binası
                </SelectItem>

                <SelectItem value="office">
                  Ofis
                </SelectItem>

                <SelectItem value="education">
                  Eğitim binası
                </SelectItem>

                <SelectItem value="healthcare">
                  Sağlık yapısı
                </SelectItem>

                <SelectItem value="residential">
                  Konut
                </SelectItem>

                <SelectItem value="commercial">
                  Ticari yapı
                </SelectItem>

                <SelectItem value="mixed">
                  Karma kullanım
                </SelectItem>

                <SelectItem value="other">
                  Diğer
                </SelectItem>
              </SelectContent>
            </Select>

            <FieldError
              errors={state.fieldErrors?.buildingType}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="totalConstructionArea">
              Toplam inşaat alanı (m²)
            </Label>

            <Input
              id="totalConstructionArea"
              name="totalConstructionArea"
              type="number"
              min="0"
              step="0.01"
              placeholder="10000"
            />

            <FieldError
              errors={
                state.fieldErrors?.totalConstructionArea
              }
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="parcelArea">
              Parsel alanı (m²)
            </Label>

            <Input
              id="parcelArea"
              name="parcelArea"
              type="number"
              min="0"
              step="0.01"
              placeholder="15000"
            />

            <FieldError
              errors={state.fieldErrors?.parcelArea}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="floorCount">
              Kat sayısı
            </Label>

            <Input
              id="floorCount"
              name="floorCount"
              type="number"
              min="1"
              step="1"
              placeholder="8"
            />

            <FieldError
              errors={state.fieldErrors?.floorCount}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="mainFacadeDirection">
              Ana cephe yönü
            </Label>

            <Select name="mainFacadeDirection">
              <SelectTrigger id="mainFacadeDirection">
                <SelectValue placeholder="Yön seçin" />
              </SelectTrigger>

              <SelectContent>
                <SelectItem value="north">Kuzey</SelectItem>
                <SelectItem value="northeast">
                  Kuzeydoğu
                </SelectItem>
                <SelectItem value="east">Doğu</SelectItem>
                <SelectItem value="southeast">
                  Güneydoğu
                </SelectItem>
                <SelectItem value="south">Güney</SelectItem>
                <SelectItem value="southwest">
                  Güneybatı
                </SelectItem>
                <SelectItem value="west">Batı</SelectItem>
                <SelectItem value="northwest">
                  Kuzeybatı
                </SelectItem>
              </SelectContent>
            </Select>

            <FieldError
              errors={
                state.fieldErrors?.mainFacadeDirection
              }
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Hedef ve bütçe</CardTitle>
          <CardDescription>
            Ön değerlendirme ve senaryo analizlerinde
            kullanılacak hedefleri belirleyin.
          </CardDescription>
        </CardHeader>

        <CardContent className="grid gap-5 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="targetCertificateLevel">
              Hedef sertifika seviyesi
            </Label>

            <Select name="targetCertificateLevel">
              <SelectTrigger id="targetCertificateLevel">
                <SelectValue placeholder="Hedef seçin" />
              </SelectTrigger>

              <SelectContent>
                <SelectItem value="pass">
                  Asgari uygunluk
                </SelectItem>

                <SelectItem value="good">
                  İyi
                </SelectItem>

                <SelectItem value="very_good">
                  Çok iyi
                </SelectItem>

                <SelectItem value="national_excellence">
                  Ulusal üstünlük
                </SelectItem>
              </SelectContent>
            </Select>

            <FieldError
              errors={
                state.fieldErrors?.targetCertificateLevel
              }
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="estimatedBudget">
              Tahmini proje bütçesi (TL)
            </Label>

            <Input
              id="estimatedBudget"
              name="estimatedBudget"
              type="number"
              min="0"
              step="0.01"
              placeholder="50000000"
            />

            <FieldError
              errors={state.fieldErrors?.estimatedBudget}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        <Button variant="outline" asChild>
          <Link href="/dashboard">İptal</Link>
        </Button>

        <CreateProjectSubmit />
      </div>
    </form>
  );
}