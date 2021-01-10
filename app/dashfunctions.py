import dateutil.parser as dparser


class TimeFunctions():
    def timedelta(t1, t2):
        #previously delta(t1, t2)
        """Provides the timedelta between two datetime values in minutes"""
        try:
            d1 = dparser.parse(t1, fuzzy=True)
            d2 = dparser.parse(t2, fuzzy=True)
            factors = (60, 1, 1/60)
            duration = str((d2 - d1))
            duration_minutes = sum(i*j for i, j in zip(map(int, duration.split(':')), factors))
            return str(round(duration_minutes))
        except:
            return 0

    def sort_by_date(list_obj):
        """Sorts a list by date in decending order"""
        try:
            list_obj.sort(key = lambda x:x['date'])
        except (KeyError, TypeError) as e:
            pass

class InputFunctions():
    """Set of functions to modify inputs (string, dict list) to a desired format."""

    def safeget(dct, *keys, na_value='NA'):
        """Get dictionary values without keyerrors.
        dct = target dict, *keys one or mutiple (if nested) keys,
        na_value is value to return in case of an error."""

        for key in keys:
            try:
                dct = dct[key]
            except (KeyError, TypeError) as e:
                return na_value
        return dct

    def try_it(input_key, na_val="NA"):

        try:
            if input_key:
                return input_key
            else:
                return na_val
        except:
            return na_val

    def list_to_string(s):
        """Transforms a list in to a string"""
        try:
            str1 = " "
            return (str1.join(s))
        except (KeyError, TypeError) as e:
            return 'NA'

    def split_it(it, split_char, split_index):
        """Splits ay a given point and returns the remainder"""
        try:
            if type(it) is str:
                return it.split(split_char)[split_index]
        except (KeyError, TypeError) as e:
            return 'NA'

    def get_tag(list_obj, tag):
        """Returns True if the given tag is in the list, otherwise False"""
        if list_obj:
            return tag in list_obj
        else:
            return False



class CostFunctions():
    """Set of functions to determine cost values, or process inputs in order to
    calculate cost values"""

    def def_two_men(val_a, val_b, na_val):
        """Define whether a route is executed by one or two persons"""
        if val_a == na_val and val_b == na_val:
            return '2mans'
            # return True
        elif val_a != na_val and val_b != na_val:
            return '2mans'
            # return True
        elif val_b != na_val:
            return '2mans'
            # return True
        else:
            return '1mans'
            # return False

    def rev_exp(driver, trailer, trailer_val, bool, costs_oneman, costs_twomen, stops, stop_rev, duration, rev_min, act_dur, loading_time, unloading_time):
        exp_costs = 0

        if driver == trailer_val and trailer == trailer_val:
            exp_costs = round(costs_twomen * float(duration), 2)
        elif trailer != trailer_val:
            exp_costs = round(costs_twomen * float(duration), 2)
        else:
            exp_costs = round(costs_oneman * float(duration), 2)


        rev = round(float(stops) * stop_rev + (float(act_dur) - float(loading_time) - float(unloading_time)) * rev_min, 2)

        try:
            margin = round(((rev - exp_costs) / rev), 2)
        except ZeroDivisionError:
            margin = 0

        return exp_costs, rev, margin

    def exp_costs(one_or_two, planned_duration, costs_oneman, costs_twomen):
        """calculate the expected costs
        planned_duration * one or two man * costs for one or two
        """
        if one_or_two == '1mans':
            return round((int(planned_duration) * float(costs_oneman)), 2)
        elif one_or_two == '2mans':
            return round((int(planned_duration) * float(costs_twomen)), 2)
        else:
            return 0

    def margin(cost, rev, as_percentage=True):
        cost = float(cost)
        rev = float(rev)

        try:
            if as_percentage is True:
                return round(((rev-cost)/rev)*100, 2)
            else:
                return round(((rev-cost)/rev), 2)
        except:
            return 0


    def totals(list, object_to_sum):
        try:
            total = 0
            for i in list:
                total += float(i[object_to_sum])

            return round(total, 2)
        except TypeError:
            return 'NA'


    def ind_stop_rev(type_dict, stop_type, one_or_two, account, rev_per_min, stop_mins):

        try:
            ind_rev = 0
            if account != None:
                if stop_type == 'Magazijn Ophalen':
                    ind_rev = 10
                elif one_or_two == '1mans':
                    ind_rev = type_dict.get(stop_type, 0) * 40 + stop_mins * rev_per_min
                elif one_or_two == '2mans':
                    ind_rev = type_dict.get(stop_type, 0) * 50 + stop_mins * rev_per_min
                else:
                    ind_rev = 0
            return ind_rev
        except:
            return 0
