
// Enum for page titles
export enum PageTitle {
  Home = "Home",
  Templates = "Templates",
  AgreementGenerator = "Agreement Generator",
  Contact = "Contact Us",
}

// Tooltip descriptions for different agreement statuses
export const statusTooltips: Record<string, string> = {
  APPROVED: "Approved by all involved parties",
  PROCESSING: "Awaiting action from one or more parties",
  REJECTED: "Rejected by one or more parties",
  EXPIRED: "No action taken by one or more parties",
  FAILED: "Failed due to connection issue",
};
