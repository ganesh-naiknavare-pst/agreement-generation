import {
  createContext,
  useContext,
  ReactNode,
  useEffect,
  useState,
  useRef,
} from "react";
import useApi, { BackendEndpoints } from "./useApi";
import { useParams, useSearchParams } from "react-router-dom";
import { Agreement, TemplateAgreement } from "../types/types";
import { useUser } from "@clerk/clerk-react";
export type UserData = {
  id: number;
  userId: string;
  agreementId: number;
  status: string;
};

interface UserContextType {
  rentAgreementUser: UserData | null;
  getRentAgreementUser: (method: {}) => Promise<void>;
  TemplateAgreementUser: UserData | null;
  getTemplateAgreementUser: (method: {}) => Promise<void>;
  setStatus: React.Dispatch<React.SetStateAction<string | null>>;
  status: string | null;
  loadRentAgreemntUser: boolean;
  loadTemplateAgreemntUser: boolean;
}

const UserContext = createContext<UserContextType>({
  rentAgreementUser: null,
  getRentAgreementUser: () => Promise.resolve(),
  TemplateAgreementUser: null,
  getTemplateAgreementUser: () => Promise.resolve(),
  setStatus: () => {},
  status: null,
  loadRentAgreemntUser: false,
  loadTemplateAgreemntUser: false,
});

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const hasFetchedRef = useRef(false);
  const { user } = useUser();
  const {
    data: rentAgreementUser,
    fetchData: getRentAgreementUser,
    loading: loadRentAgreemntUser,
  } = useApi<UserData>(BackendEndpoints.GetRentAgreementUser);
  const {
    data: TemplateAgreementUser,
    fetchData: getTemplateAgreementUser,
    loading: loadTemplateAgreemntUser,
  } = useApi<UserData>(BackendEndpoints.GetTemplateAgreementUSer);
  const { fetchData: updateClerkUserIds } = useApi<
    Agreement[] | TemplateAgreement[]
  >(BackendEndpoints.UpdateClerkUserIds);
  const param = useParams();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    if (param.id && param.agreementId && !hasFetchedRef.current) {
      const agreement_id = param.agreementId;
      const user_id = param.id;
      const isRentAgreement = searchParams.get("type") === "rent";

      const agreementUserFetcher = isRentAgreement
        ? getRentAgreementUser
        : getTemplateAgreementUser;

      agreementUserFetcher({
        method: "GET",
        params: { agreement_id, user_id },
      });

      updateClerkUserIds({
        method: "POST",
        data: {
          agreement_id,
          user_id: user?.id,
          is_template: !isRentAgreement,
        },
      });
      hasFetchedRef.current = true;
    }
  }, []);

  return (
    <UserContext.Provider
      value={{
        rentAgreementUser,
        getRentAgreementUser,
        TemplateAgreementUser,
        getTemplateAgreementUser,
        setStatus,
        status,
        loadRentAgreemntUser,
        loadTemplateAgreemntUser,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const useUserState = () => useContext(UserContext);
