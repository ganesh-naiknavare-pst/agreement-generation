export interface Agreement {
  id: number;
  address: string;
  city: string;
  agreementPeriod: string[];
  pdf: string;
  owner: {
    name: string;
    email: string;
  }[];
  tenants: {
    name: string;
    email: string;
  }[];
  status: string;
  clerkUserIds: string[];
}

export interface TemplateAgreement {
  id: number;
  address: string;
  city: string;
  createdAt: string;
  pdf: string;
  authority: {
    email: string;
  }[];
  participant: {
    email: string;
  }[];
  status: string;
  clerkUserIds: string[];
}
