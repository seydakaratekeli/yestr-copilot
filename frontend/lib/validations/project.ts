import { z } from "zod";

const optionalPositiveNumber = z.preprocess(
  (value) => {
    if (value === "" || value === null || value === undefined) {
      return undefined;
    }

    return Number(value);
  },
  z
    .number({
      message: "Geçerli bir sayı girin.",
    })
    .positive("Değer sıfırdan büyük olmalıdır.")
    .optional(),
);

const optionalPositiveInteger = z.preprocess(
  (value) => {
    if (value === "" || value === null || value === undefined) {
      return undefined;
    }

    return Number(value);
  },
  z
    .number({
      message: "Geçerli bir sayı girin.",
    })
    .int("Tam sayı girin.")
    .positive("Değer sıfırdan büyük olmalıdır.")
    .optional(),
);

export const projectSchema = z.object({
  name: z
    .string()
    .trim()
    .min(3, "Proje adı en az 3 karakter olmalıdır.")
    .max(200, "Proje adı en fazla 200 karakter olabilir."),

  description: z
    .string()
    .trim()
    .max(2000, "Açıklama en fazla 2000 karakter olabilir.")
    .optional(),

  city: z
    .string()
    .trim()
    .max(100, "Şehir adı çok uzun.")
    .optional(),

  district: z
    .string()
    .trim()
    .max(100, "İlçe adı çok uzun.")
    .optional(),

  buildingType: z
    .string()
    .trim()
    .max(100, "Bina türü çok uzun.")
    .optional(),

  projectType: z.enum(["new_building", "existing_building"]),

  totalConstructionArea: optionalPositiveNumber,
  parcelArea: optionalPositiveNumber,
  floorCount: optionalPositiveInteger,

  mainFacadeDirection: z
    .string()
    .trim()
    .max(30)
    .optional(),

  targetCertificateLevel: z
    .string()
    .trim()
    .max(50)
    .optional(),

  estimatedBudget: optionalPositiveNumber,
});

export type ProjectFormValues = z.infer<typeof projectSchema>;