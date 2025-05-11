class ConversionHelper:
    @staticmethod
    def celsius_to_kelvin(celsius):
        return celsius + 273.15

    @staticmethod
    def kelvin_to_celsius(kelvin):
        return kelvin - 273.15

    @staticmethod
    def kpa_to_pa(kpa):
        return kpa * 1e3

    @staticmethod
    def pa_to_kpa(pa):
        return pa / 1e3

    @staticmethod
    def kgph_to_kgps(kgph):
        return kgph / 3600

    @staticmethod
    def kgps_to_kgph(kgps):
        return kgps * 3600

    @staticmethod
    def kj_to_j(kj):
        return kj * 1e3

    @staticmethod
    def j_to_kj(joules):
        return joules / 1e3

    @staticmethod
    def m3h_to_m3s(m3h):
        return m3h / 3600

    @staticmethod
    def m3s_to_m3h(m3s):
        return m3s * 3600
