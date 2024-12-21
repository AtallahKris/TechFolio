classdef Matlab_Project < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                   matlab.ui.Figure
        ExitButton                 matlab.ui.control.Button
        DarkLabel                  matlab.ui.control.Label
        Switch                     matlab.ui.control.Switch
        LightLabel                 matlab.ui.control.Label
        SettingsButton             matlab.ui.control.Button
        SubtotalwTaxField          matlab.ui.control.NumericEditField
        SubtotalwTaxLabel          matlab.ui.control.Label
        DishoftheDayDropDown       matlab.ui.control.DropDown
        DishoftheDayDropDownLabel  matlab.ui.control.Label
        SubtotalField              matlab.ui.control.NumericEditField
        SubtotalLabel              matlab.ui.control.Label
        PL17                       matlab.ui.control.Label
        S17                        matlab.ui.control.Spinner
        P17                        matlab.ui.control.Label
        O17                        matlab.ui.control.Label
        Copyright                  matlab.ui.control.Label
        S8                         matlab.ui.control.Spinner
        PL8                        matlab.ui.control.Label
        P8                         matlab.ui.control.Label
        O8                         matlab.ui.control.Label
        PL16                       matlab.ui.control.Label
        S16                        matlab.ui.control.Spinner
        P16                        matlab.ui.control.Label
        O16                        matlab.ui.control.Label
        S7                         matlab.ui.control.Spinner
        PL7                        matlab.ui.control.Label
        P7                         matlab.ui.control.Label
        O7                         matlab.ui.control.Label
        TipsSlider                 matlab.ui.control.Slider
        TipsSliderLabel            matlab.ui.control.Label
        PL15                       matlab.ui.control.Label
        S15                        matlab.ui.control.Spinner
        P15                        matlab.ui.control.Label
        O15                        matlab.ui.control.Label
        S6                         matlab.ui.control.Spinner
        PL6                        matlab.ui.control.Label
        P6                         matlab.ui.control.Label
        O6                         matlab.ui.control.Label
        CopyrightNote              matlab.ui.control.Label
        QRCaption                  matlab.ui.control.Label
        PL14                       matlab.ui.control.Label
        S14                        matlab.ui.control.Spinner
        P14                        matlab.ui.control.Label
        O14                        matlab.ui.control.Label
        S5                         matlab.ui.control.Spinner
        PL5                        matlab.ui.control.Label
        P5                         matlab.ui.control.Label
        O5                         matlab.ui.control.Label
        CalcNote                   matlab.ui.control.Label
        PL13                       matlab.ui.control.Label
        S13                        matlab.ui.control.Spinner
        P13                        matlab.ui.control.Label
        O13                        matlab.ui.control.Label
        S4                         matlab.ui.control.Spinner
        PL4                        matlab.ui.control.Label
        P4                         matlab.ui.control.Label
        O4                         matlab.ui.control.Label
        AddressLabel               matlab.ui.control.Label
        CalculationsLabel          matlab.ui.control.Label
        SeafoodLabel               matlab.ui.control.Label
        SandwichesLabel            matlab.ui.control.Label
        PromoCodeNote              matlab.ui.control.Label
        SoupDropDown               matlab.ui.control.DropDown
        SoupDropDown_3Label        matlab.ui.control.Label
        S21                        matlab.ui.control.Spinner
        PL21                       matlab.ui.control.Label
        P21                        matlab.ui.control.Label
        O21                        matlab.ui.control.Label
        PL12                       matlab.ui.control.Label
        S12                        matlab.ui.control.Spinner
        PromoCodeSubmit            matlab.ui.control.Button
        P12                        matlab.ui.control.Label
        O12                        matlab.ui.control.Label
        PromoCodeField             matlab.ui.control.EditField
        CurrencyDropDown           matlab.ui.control.DropDown
        CurrencyDropDownLabel      matlab.ui.control.Label
        S20                        matlab.ui.control.Spinner
        PL20                       matlab.ui.control.Label
        P20                        matlab.ui.control.Label
        O20                        matlab.ui.control.Label
        PL11                       matlab.ui.control.Label
        S11                        matlab.ui.control.Spinner
        P11                        matlab.ui.control.Label
        O11                        matlab.ui.control.Label
        S3                         matlab.ui.control.Spinner
        PL3                        matlab.ui.control.Label
        P3                         matlab.ui.control.Label
        O3                         matlab.ui.control.Label
        S19                        matlab.ui.control.Spinner
        PL19                       matlab.ui.control.Label
        P19                        matlab.ui.control.Label
        O19                        matlab.ui.control.Label
        PL10                       matlab.ui.control.Label
        S10                        matlab.ui.control.Spinner
        P10                        matlab.ui.control.Label
        O10                        matlab.ui.control.Label
        AddPromoCodeorCouponEditFieldLabel  matlab.ui.control.Label
        S2                         matlab.ui.control.Spinner
        PL2                        matlab.ui.control.Label
        P2                         matlab.ui.control.Label
        LanguageDropDown           matlab.ui.control.DropDown
        O2                         matlab.ui.control.Label
        LanguageDropDownLabel      matlab.ui.control.Label
        S18                        matlab.ui.control.Spinner
        PL18                       matlab.ui.control.Label
        P18                        matlab.ui.control.Label
        QR                         matlab.ui.control.Image
        O18                        matlab.ui.control.Label
        PL9                        matlab.ui.control.Label
        S9                         matlab.ui.control.Spinner
        P9                         matlab.ui.control.Label
        O9                         matlab.ui.control.Label
        S1                         matlab.ui.control.Spinner
        PL1                        matlab.ui.control.Label
        P1                         matlab.ui.control.Label
        O1                         matlab.ui.control.Label
        BeveragesLabel             matlab.ui.control.Label
        SaladsLabel                matlab.ui.control.Label
        StartersLabel              matlab.ui.control.Label
        UnderTitle                 matlab.ui.control.Label
        UnderTitleSettings         matlab.ui.control.Label
        DatePicker                 matlab.ui.control.DatePicker
        DateDatePickerLabel        matlab.ui.control.Label
        LogoLight                  matlab.ui.control.Image
        LogoDark                   matlab.ui.control.Image
        Title                      matlab.ui.control.Label
    end

    methods (Access = public)
        function TOTAL(app)
            if app.CurrencyDropDown.Value == "US Dollar"
                app.SubtotalField.Value = (app.S1.Value*5.99 + app.DishoftheDayDropDown.Value + app.SoupDropDown.Value + app.S2.Value*7.99 + app.S3.Value*8.99  +...
                    app.S4.Value*8.99 + app.S5.Value*8.99  + app.S6.Value*7.99 + app.S7.Value*10.99 + app.S8.Value*9.99  + app.S9.Value*8.99 + app.S10.Value*9.99 + ...
                    app.S11.Value*11.99 + app.S12.Value*12.99 + app.S13.Value*18.99 + app.S14.Value*15.99 + app.S15.Value*12.99 + app.S16.Value*20.99 + ...
                    app.S17.Value*17.99 + app.S18.Value*1.49 + app.S19.Value*2.99 + app.S20.Value*3.49 + app.S21.Value*4.99);
                app.SubtotalField.Value = app.SubtotalField.Value + (app.SubtotalField.Value*(app.TipsSlider.Value/100));
                app.SubtotalwTaxField.Value = (app.SubtotalField.Value * 0.05) + app.SubtotalField.Value;
            end

            if app.CurrencyDropDown.Value == "LBP"
                app.SubtotalField.Value = (app.S1.Value*5.99*96 + app.DishoftheDayDropDown.Value + app.SoupDropDown.Value + app.S2.Value*7.99*96 + app.S3.Value*8.99*96  +...
                    app.S4.Value*8.99*96 + app.S5.Value*8.99*96  + app.S6.Value*7.99*96 + app.S7.Value*10.99*96 + app.S8.Value*9.99*96  + app.S9.Value*8.99*96 + app.S10.Value*9.99*96 + ...
                    app.S11.Value*11.99*96 + app.S12.Value*12.99*96 + app.S13.Value*18.99*96 + app.S14.Value*15.99*96 + app.S15.Value*12.99*96 + app.S16.Value*20.99*96 + ...
                    app.S17.Value*17.99*96 + app.S18.Value*1.49*96 + app.S19.Value*2.99*96 + app.S20.Value*3.49*96 + app.S21.Value*4.99*96);
                app.SubtotalField.Value = app.SubtotalField.Value + (app.SubtotalField.Value*(app.TipsSlider.Value/100));
                app.SubtotalwTaxField.Value = (app.SubtotalField.Value * 0.05) + app.SubtotalField.Value;
            end
        end

        function updateColors(app)
            if app.Switch.Value == "L"
                % Light Mode
                app.UIFigure.Color = [0.9 0.9 0.9];

                set(app.LogoDark, 'Visible', 'on')
                set(app.LogoLight, 'Visible', 'off')

                controls = {app.SubtotalLabel, app.SubtotalwTaxLabel , app.Title, app.UnderTitle, app.StartersLabel, ...
                    app.BeveragesLabel , app.DarkLabel, app.LightLabel, app.SandwichesLabel, app.SaladsLabel, app.SeafoodLabel, app.CalculationsLabel, ...
                    app.CalcNote, app.TipsSlider, app.TipsSliderLabel, app.O1, app.O2, app.O3, ...
                    app.O4, app.O5, app.O6, app.O7, app.O8, app.O9, app.O10, app.O11, app.O12, app.O13, app.O14, app.O15, app.O16, app.O17, ...
                    app.O18, app.O19, app.O20, app.O21, app.DateDatePickerLabel, app.SoupDropDown_3Label, app.DishoftheDayDropDownLabel, ...
                    app.P1, app.P2, app.P3, app.P4, app.P5, app.P6, app.P7, app.P8, app.P9, app.P10, app.P11, app.P12, app.P13, app.P14, ...
                    app.P15, app.P16, app.P17, app.P18, app.P19, app.P20, app.P21, app.LanguageDropDownLabel, app.CurrencyDropDownLabel, ...
                    app.AddPromoCodeorCouponEditFieldLabel, app.PromoCodeNote, app.PromoCodeSubmit, app.PromoCodeField, ...
                    app.AddressLabel, app.LanguageDropDown, app.CurrencyDropDown, ...
                    app.QRCaption, app.Copyright, app.UnderTitleSettings, app.CopyrightNote, app.PL1, app.PL2, app.PL3, ...
                    app.PL4, app.PL5, app.PL6, app.PL7, app.PL8, app.PL9, app.PL10, app.PL11, app.PL12, app.PL13, app.PL14, app.PL15, ...
                    app.PL16, app.PL17, app.PL18, app.PL19, app.PL20, app.PL21};

                for i = 1:numel(controls)
                    controls{i}.FontColor = [0.3 0.3 0.3];
                end
            else
                % Dark Mode
                app.UIFigure.Color = [0.2 0.2 0.2];

                set(app.LogoDark, 'Visible', 'off')
                set(app.LogoLight, 'Visible', 'on')

                controls = {app.BeveragesLabel, app.SubtotalLabel, app.SubtotalwTaxLabel , app.Title, app.UnderTitle, app.StartersLabel, ...
                    app.DarkLabel, app.LightLabel, app.SandwichesLabel, app.SaladsLabel, app.SeafoodLabel, app.CalculationsLabel, ...
                    app.CalcNote, app.TipsSlider, app.TipsSliderLabel, app.O1, app.O2, app.O3, ...
                    app.O4, app.O5, app.O6, app.O7, app.O8, app.O9, app.O10, app.O11, app.O12, app.O13, app.O14, app.O15, app.O16, ...
                    app.O17, app.O18, app.O19, app.O20, app.O21, app.DateDatePickerLabel, app.SoupDropDown_3Label, ...
                    app.DishoftheDayDropDownLabel, app.P1, app.P2, app.P3, app.P4, app.P5, app.P6, app.P7, app.P8, ...
                    app.P9, app.P10, app.P11, app.P12, app.P13, app.P14, app.P15, app.P16, app.P17, app.P18, app.P19, ...
                    app.P20, app.P21, app.LanguageDropDownLabel, app.CurrencyDropDownLabel, app.AddPromoCodeorCouponEditFieldLabel, ...
                    app.PromoCodeNote, app.AddressLabel, app.QRCaption, ...
                    app.Copyright, app.UnderTitleSettings, app.CopyrightNote, app.PL1, app.PL2, app.PL3, app.PL4, app.PL5, app.PL6, app.PL7, app.PL8, ...
                    app.PL9, app.PL10, app.PL11, app.PL12, app.PL13, app.PL14, app.PL15, app.PL16, app.PL17, app.PL18, app.PL19, app.PL20, app.PL21};

                for i = 1:numel(controls)
                    controls{i}.FontColor = [0.8 0.8 0.8];
                end
            end
        end
    end


    % Callbacks that handle component events
    methods (Access = private)

        % Button pushed function: ExitButton
        function ExitButtonPushed(app, event)
            delete(app.UIFigure) % Close the appwindow
        end

        % Value changed function: DatePicker
        function DatePickerValueChanged(app, event)
            value = app.DatePicker.Value;
            daynb = weekday(value);
            if app.CurrencyDropDown.Value == "US Dollar"
                switch (daynb)
                    case 1
                        app.DishoftheDayDropDown.Items = ["< Sunday >" "Vegetarian: Roasted Vegetable Salad ($11)" "Meat: Roast Beef w Roasted Potatoes ($18)"];
                        app.DishoftheDayDropDown.ItemsData = [0 11 18];
                    case 2
                        app.DishoftheDayDropDown.Items = ["< Monday >" "Vegetarian: Chickpea Curry ($13)" "Meat: Grilled Chicken w Rice ($15)"];
                        app.DishoftheDayDropDown.ItemsData = [0 13 15];
                    case 3
                        app.DishoftheDayDropDown.Items = ["< Tuesday >" "Vegetarian: Falafelwrap ($10)" "Meat: Beef Burger w Fries ($14)"];
                        app.DishoftheDayDropDown.ItemsData = [0 10 14];
                    case 4
                        app.DishoftheDayDropDown.Items = ["< Wednesday >" "Vegetarian: Veggie Quesadilla ($11)" "Meat: Steak Fajitas ($17)"];
                        app.DishoftheDayDropDown.ItemsData = [0 11 17];
                    case 5
                        app.DishoftheDayDropDown.Items = ["< Thursday >" "Vegetarian: Spinach and Ricotta Ravioli ($12)" "Meat: Lamb Chops w Mashed Potatoes ($20)"];
                        app.DishoftheDayDropDown.ItemsData = [0 12 20];
                    case 6
                        app.DishoftheDayDropDown.Items = ["< Friday >" "Vegetarian: Margherita Pizza ($13)" "Meat: Philly Cheesesteak Sandwich ($11)"];
                        app.DishoftheDayDropDown.ItemsData = [0 13 11];
                    case 7
                        app.DishoftheDayDropDown.Items = ["< Saturday >" "Vegetarian: Grilled Veggie Skewers ($14)" "Meat: BBQ Ribs w Corn on the Cob ($19)"];
                        app.DishoftheDayDropDown.ItemsData = [0 14 19];
                end
                return;
            end

            if app.CurrencyDropDown.Value == "LBP"
                switch (daynb)
                    case 1
                        app.DishoftheDayDropDown.Items = ["< Sunday >" "Vegetarian: Roasted Vegetable Salad (1056LBP)" "Meat: Roast Beef w Roasted Potatoes (1728LBP)"];
                        app.DishoftheDayDropDown.ItemsData = [0 1056 1728];
                    case 2
                        app.DishoftheDayDropDown.Items = ["< Monday >" "Vegetarian: Chickpea Curry (1248LBP)" "Meat: Grilled Chicken w Rice (1440LBP)"];
                        app.DishoftheDayDropDown.ItemsData = [0 1248 1440];
                    case 3
                        app.DishoftheDayDropDown.Items = ["< Tuesday >" "Vegetarian: Falafelwrap (960LBP)" "Meat: Beef Burger w Fries (1344LBP)"];
                        app.DishoftheDayDropDown.ItemsData = [0 960 1344];
                    case 4
                        app.DishoftheDayDropDown.Items = ["< Wednesday >" "Vegetarian: Veggie Quesadilla (1056LBP)" "Meat: Steak Fajitas (1632LBP)"];
                        app.DishoftheDayDropDown.ItemsData = [0 1056 1632];
                    case 5
                        app.DishoftheDayDropDown.Items = ["< Thursday >" "Vegetarian: Spinach and Ricotta Ravioli (1152LBP)" "Meat: Lamb Chops w Mashed Potatoes (1920LBP)"];
                        app.DishoftheDayDropDown.ItemsData = [0 1152 1920];
                    case 6
                        app.DishoftheDayDropDown.Items = ["< Friday >" "Vegetarian: Margherita Pizza (1248LBP)" "Meat: Philly Cheesesteak Sandwich (1056LBP)"];
                        app.DishoftheDayDropDown.ItemsData = [0 1248 1056];
                    case 7
                        app.DishoftheDayDropDown.Items = ["< Saturday >" "Vegetarian: Grilled Veggie Skewers (1344LBP)" "Meat: BBQ Ribs w Corn on the Cob (1824LBP)"];
                        app.DishoftheDayDropDown.ItemsData = [0 1344 1824];
                end
                return;
            end
        end

        % Callback function: DishoftheDayDropDown, S1, S10, S11, S12, S13, 
        % ...and 19 other components
        function S1ValueChanged(app, event)
            TOTAL(app);
        end

        % Value changed function: Switch
        function SwitchValueChanged(app, event)
            updateColors(app);
        end

        % Button pushed function: SettingsButton
        function SettingsButtonPushed(app, event)

            controls = {app.SubtotalLabel, app.SubtotalwTaxLabel , app.StartersLabel, ...
                app.SandwichesLabel, app.SaladsLabel, app.SeafoodLabel, app.CalculationsLabel, ...
                app.CalcNote, app.TipsSlider, app.TipsSliderLabel, ...
                app.UnderTitle, app.O1, app.O2, app.O3, app.O4, app.O5, app.O6, app.O7, app.O8, app.O9, ...
                app.O10, app.O11, app.O12, app.O13, app.O14, app.O15, app.O16, app.O17, app.O18, app.O19, ...
                app.O20, app.O21, app.DateDatePickerLabel, app.SoupDropDown_3Label, app.SoupDropDown , ...
                app.DishoftheDayDropDown , app.DishoftheDayDropDownLabel, app.P1, app.P2, app.P3, app.P4, ...
                app.P5, app.P6, app.P7, app.P8, app.P9, app.P10, app.P11, app.P12, app.P13, app.P14, app.P15, ...
                app.P16, app.P17, app.P18, app.P19, app.P20, app.P21, app.PL1, app.PL2, app.S1, app.BeveragesLabel, ...
                app.DatePicker, app.SubtotalField, app.SubtotalwTaxField, app.S2, app.S3, app.S4, app.S5, ...
                app.S6, app.S7, app.S8, app.S9, app.S10, app.S11, app.S12, app.S13, app.S14, app.S15, app.S16, app.S17, ...
                app.S18, app.S19, app.S20, app.S21, app.PL3, app.PL4, app.PL5, app.PL6, app.PL7, app.PL8, app.PL9, ...
                app.PL10, app.PL11, app.PL12, app.PL13, app.PL14, app.PL15, app.PL16, app.PL17, app.PL18, app.PL19, app.PL20, app.PL21};
           
            controls2 = {app.LanguageDropDownLabel, app.CurrencyDropDownLabel, app.AddPromoCodeorCouponEditFieldLabel, ...
                app.PromoCodeNote, app.PromoCodeSubmit, app.PromoCodeField, app.QR, ...
                app.AddressLabel, app.LanguageDropDown, ...
                app.CurrencyDropDown, app.QRCaption, app.Copyright, app.UnderTitleSettings, app.CopyrightNote};

            if app.SettingsButton.Text == "Settings"
                app.SettingsButton.Text = "Back";
                for i = 1:numel(controls)
                    set(controls{i}, 'Visible', 'off')
                end
                for i = 1:numel(controls2)
                    set(controls2{i}, 'Visible', 'on')
                end
                return;
            end
            if app.SettingsButton.Text == "Back"
                app.SettingsButton.Text = "Settings";
                for i = 1:numel(controls)
                    set(controls{i}, 'Visible', 'on')
                end
                for i = 1:numel(controls2)
                    set(controls2{i}, 'Visible', 'off')
                end
                return;
            end
        end

        % Button pushed function: PromoCodeSubmit
        function PromoCodeSubmitPushed(app, event)
            input_string = app.PromoCodeField.Value;

            % Check length of string
            if length(input_string) ~= 10
                app.PromoCodeNote.Text = 'String must be exactly 10 characters long';
                return;
            end

            % Check first letter is a vowel
            if ~ismember(input_string(1), 'AEIOU')
                app.PromoCodeNote.Text = 'First letter must be a vowel';
                return;
            end

            % Check second letter is a consonant
            if ismember(input_string(2), 'AEIOU') || ~isletter(input_string(2))
                app.PromoCodeNote.Text = 'Second letter must be a consonant';
                return;
            end

            % Check fourth letter is the same as first letter
            if input_string(4) ~= input_string(1)
                app.PromoCodeNote.Text = 'Fourth letter must be the same as the first letter';
                return;
            end

            % Check eighth letter is the digit that appears in the code
            if input_string(8) ~= input_string(3)
                app.PromoCodeNote.Text = 'Eighth letter must be the digit that appears in the code';
                return;
            end

            % Check ninth letter is in the word "CODE"
            if ~ismember(input_string(9), 'CODE')
                app.PromoCodeNote.Text = 'Ninth letter must be in the word "CODE"';
                return;
            end

            % Check tenth letter is in the word "DISCOUNT"
            if ~ismember(input_string(10), 'DISCOUNT')
                app.PromoCodeNote.Text = 'Tenth letter must be in the word "DISCOUNT"';
                return;
            end
            app.SubtotalField.Value = app.SubtotalField.Value*0.9;
            app.SubtotalwTaxField.Value = app.SubtotalwTaxField.Value*0.9;

            app.PromoCodeNote.Text = 'Promo Code Activated';
        end

        % Value changed function: CurrencyDropDown
        function CurrencyDropDownValueChanged(app, event)

            PLcontrol = {app.PL1, app.PL2, app.PL3, app.PL4, app.PL5, ...
                app.PL6, app.PL7, app.PL8, app.PL9, app.PL10, app.PL11, ...
                app.PL12, app.PL13, app.PL14, app.PL15, app.PL16, app.PL17, ...
                app.PL18, app.PL19, app.PL20, app.PL21};

            DatePickerValueChanged(app, event);
            app.SubtotalField.Value = 0;
            app.SubtotalwTaxField.Value = 0;

            if app.CurrencyDropDown.Value == "LBP"
                for i = 1:numel(PLcontrol)
                    PLcontrol{i}.Text = "LBP";
                end

                app.UnderTitle.Text = sprintf("Current Rate: 1 USD = 96,000 LBP\n" + ...
                    "Values shown are multipled by 1,000");

                app.P1.Text = "575";
                app.P2.Text = "767";
                app.P3.Text = "863";
                app.P4.Text = "863";
                app.P5.Text = "863";
                app.P6.Text = "767";
                app.P7.Text = "1,055";
                app.P8.Text = "959";
                app.P9.Text = "863";
                app.P10.Text = "959";
                app.P11.Text = "1,151";
                app.P12.Text = "1,247";
                app.P13.Text = "1,823";
                app.P14.Text = "1,535";
                app.P15.Text = "1,247";
                app.P16.Text = "2,015";
                app.P17.Text = "1,727";
                app.P18.Text = "143";
                app.P19.Text = "287";
                app.P20.Text = "355";
                app.P21.Text = "479";

                app.SoupDropDown.Items = ["< None >" "Asparagus (960LBP)" "Chinese Noodle (672LBP)" "Egg Drop (768LBP)" "Fish and Tofu (1056LBP)" "Hototay (576LBP)"];
                app.SoupDropDown.ItemsData = [0 960 672 768 1056 576];

                app.SubtotalField.ValueDisplayFormat = "%11.4g LBP";
                app.SubtotalwTaxField.ValueDisplayFormat = "%11.4g LBP";
            end

            if app.CurrencyDropDown.Value == "US Dollar"
                for i = 1:numel(PLcontrol)
                    PLcontrol{i}.Text = "$";
                end
                app.UnderTitle.Text = ("*Settings for additional options ");

                app.P1.Text = "5.99";
                app.P2.Text = "7.99";
                app.P3.Text = "8.99";
                app.P4.Text = "8.99";
                app.P5.Text = "8.99";
                app.P6.Text = "7.99";
                app.P7.Text = "10.99";
                app.P8.Text = "9.99";
                app.P9.Text = "8.99";
                app.P10.Text = "9.99";
                app.P11.Text = "11.99";
                app.P12.Text = "12.99";
                app.P13.Text = "18.99";
                app.P14.Text = "15.99";
                app.P15.Text = "12.99";
                app.P16.Text = "20.99";
                app.P17.Text = "17.99";
                app.P18.Text = "1.49";
                app.P19.Text = "2.99";
                app.P20.Text = "3.49";
                app.P21.Text = "4.99";

                app.SoupDropDown.Items = ["< None >" "Asparagus (10$)" "Chinese Noodle (7$)" "Egg Drop (8$)" "Fish and Tofu (11$)" "Hototay (6$)"];
                app.SoupDropDown.ItemsData = [0 10 7 8 11 6];

                app.SubtotalField.ValueDisplayFormat = "%11.4g $";
                app.SubtotalwTaxField.ValueDisplayFormat = "%11.4g $";
            end
        end
    end

    % Component initialization
    methods (Access = private)

        % Create UIFigure and components
        function createComponents(app)

            % Get the file path for locating images
            pathToMLAPP = fileparts(mfilename('fullpath'));

            % Create UIFigure and hide until all components are created
            app.UIFigure = uifigure('Visible', 'off');
            app.UIFigure.Color = [0.902 0.902 0.902];
            app.UIFigure.Position = [100 100 1050 700];
            app.UIFigure.Name = 'MATLAB App';
            app.UIFigure.WindowStyle = 'modal';
            app.UIFigure.Pointer = 'crosshair';

            % Create Title
            app.Title = uilabel(app.UIFigure);
            app.Title.HorizontalAlignment = 'center';
            app.Title.FontName = 'Segoe UI';
            app.Title.FontSize = 48;
            app.Title.FontWeight = 'bold';
            app.Title.FontColor = [0.149 0.149 0.149];
            app.Title.Position = [1 623 1050 67];
            app.Title.Text = 'Mat''s Lab';

            % Create LogoDark
            app.LogoDark = uiimage(app.UIFigure);
            app.LogoDark.Position = [881 591 100 100];
            app.LogoDark.ImageSource = fullfile(pathToMLAPP, 'Icon - Black.png');

            % Create LogoLight
            app.LogoLight = uiimage(app.UIFigure);
            app.LogoLight.Visible = 'off';
            app.LogoLight.Position = [881 590 100 100];
            app.LogoLight.ImageSource = fullfile(pathToMLAPP, 'Icon - White.png');

            % Create DateDatePickerLabel
            app.DateDatePickerLabel = uilabel(app.UIFigure);
            app.DateDatePickerLabel.HorizontalAlignment = 'center';
            app.DateDatePickerLabel.FontSize = 16;
            app.DateDatePickerLabel.FontColor = [0.149 0.149 0.149];
            app.DateDatePickerLabel.Position = [48 639 39 22];
            app.DateDatePickerLabel.Text = 'Date';

            % Create DatePicker
            app.DatePicker = uidatepicker(app.UIFigure);
            app.DatePicker.DisplayFormat = 'dd/MMM/uuuu';
            app.DatePicker.ValueChangedFcn = createCallbackFcn(app, @DatePickerValueChanged, true);
            app.DatePicker.FontSize = 16;
            app.DatePicker.Position = [114 639 150 22];

            % Create UnderTitleSettings
            app.UnderTitleSettings = uilabel(app.UIFigure);
            app.UnderTitleSettings.HorizontalAlignment = 'center';
            app.UnderTitleSettings.FontSize = 14;
            app.UnderTitleSettings.FontWeight = 'bold';
            app.UnderTitleSettings.FontAngle = 'italic';
            app.UnderTitleSettings.FontColor = [0.149 0.149 0.149];
            app.UnderTitleSettings.Visible = 'off';
            app.UnderTitleSettings.Position = [1 577 1050 47];
            app.UnderTitleSettings.Text = {'*Go to the waiter for further help'; '**Based on Restaurant GUI SPRING 2023'};

            % Create UnderTitle
            app.UnderTitle = uilabel(app.UIFigure);
            app.UnderTitle.HorizontalAlignment = 'center';
            app.UnderTitle.FontSize = 14;
            app.UnderTitle.FontWeight = 'bold';
            app.UnderTitle.FontAngle = 'italic';
            app.UnderTitle.FontColor = [0.149 0.149 0.149];
            app.UnderTitle.Position = [1 590 1050 33];
            app.UnderTitle.Text = '*Settings for additional options ';

            % Create StartersLabel
            app.StartersLabel = uilabel(app.UIFigure);
            app.StartersLabel.HorizontalAlignment = 'center';
            app.StartersLabel.FontName = 'Segoe UI';
            app.StartersLabel.FontSize = 20;
            app.StartersLabel.FontWeight = 'bold';
            app.StartersLabel.FontColor = [0.149 0.149 0.149];
            app.StartersLabel.Position = [1 541 350 40];
            app.StartersLabel.Text = 'Starters';

            % Create SaladsLabel
            app.SaladsLabel = uilabel(app.UIFigure);
            app.SaladsLabel.HorizontalAlignment = 'center';
            app.SaladsLabel.FontName = 'Segoe UI';
            app.SaladsLabel.FontSize = 20;
            app.SaladsLabel.FontWeight = 'bold';
            app.SaladsLabel.FontColor = [0.149 0.149 0.149];
            app.SaladsLabel.Position = [351 541 350 40];
            app.SaladsLabel.Text = 'Salads';

            % Create BeveragesLabel
            app.BeveragesLabel = uilabel(app.UIFigure);
            app.BeveragesLabel.HorizontalAlignment = 'center';
            app.BeveragesLabel.FontName = 'Segoe UI';
            app.BeveragesLabel.FontSize = 20;
            app.BeveragesLabel.FontWeight = 'bold';
            app.BeveragesLabel.FontColor = [0.149 0.149 0.149];
            app.BeveragesLabel.Position = [701 541 350 40];
            app.BeveragesLabel.Text = 'Beverages';

            % Create O1
            app.O1 = uilabel(app.UIFigure);
            app.O1.FontSize = 16;
            app.O1.FontColor = [0.149 0.149 0.149];
            app.O1.Position = [41 508 132 25];
            app.O1.Text = 'Garlic Bread';

            % Create P1
            app.P1 = uilabel(app.UIFigure);
            app.P1.FontSize = 16;
            app.P1.FontColor = [0.149 0.149 0.149];
            app.P1.Position = [192 508 42 26];
            app.P1.Text = '5.99';

            % Create PL1
            app.PL1 = uilabel(app.UIFigure);
            app.PL1.HorizontalAlignment = 'center';
            app.PL1.FontSize = 16;
            app.PL1.FontWeight = 'bold';
            app.PL1.FontColor = [0.149 0.149 0.149];
            app.PL1.Position = [235 508 37 26];
            app.PL1.Text = '$';

            % Create S1
            app.S1 = uispinner(app.UIFigure);
            app.S1.Limits = [0 99];
            app.S1.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S1.FontSize = 14;
            app.S1.Position = [274 508 59 26];

            % Create O9
            app.O9 = uilabel(app.UIFigure);
            app.O9.FontSize = 16;
            app.O9.FontColor = [0.149 0.149 0.149];
            app.O9.Position = [402 507 132 25];
            app.O9.Text = 'Caesar Salad';

            % Create P9
            app.P9 = uilabel(app.UIFigure);
            app.P9.FontSize = 16;
            app.P9.FontColor = [0.149 0.149 0.149];
            app.P9.Position = [553 507 58 26];
            app.P9.Text = '8.99';

            % Create S9
            app.S9 = uispinner(app.UIFigure);
            app.S9.Limits = [0 99];
            app.S9.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S9.FontSize = 14;
            app.S9.FontColor = [0.149 0.149 0.149];
            app.S9.Position = [635 507 59 26];

            % Create PL9
            app.PL9 = uilabel(app.UIFigure);
            app.PL9.HorizontalAlignment = 'center';
            app.PL9.FontSize = 16;
            app.PL9.FontWeight = 'bold';
            app.PL9.FontColor = [0.149 0.149 0.149];
            app.PL9.Position = [596 507 37 26];
            app.PL9.Text = '$';

            % Create O18
            app.O18 = uilabel(app.UIFigure);
            app.O18.FontSize = 16;
            app.O18.FontColor = [0.149 0.149 0.149];
            app.O18.Position = [741 507 132 25];
            app.O18.Text = 'Water (2L)';

            % Create QR
            app.QR = uiimage(app.UIFigure);
            app.QR.Visible = 'off';
            app.QR.Position = [785 333 224 221];
            app.QR.ImageSource = fullfile(pathToMLAPP, '257c2b9df859f2de9e935d18583704c3.png');

            % Create P18
            app.P18 = uilabel(app.UIFigure);
            app.P18.FontSize = 16;
            app.P18.FontColor = [0.149 0.149 0.149];
            app.P18.Position = [892 507 42 26];
            app.P18.Text = '1.49';

            % Create PL18
            app.PL18 = uilabel(app.UIFigure);
            app.PL18.HorizontalAlignment = 'center';
            app.PL18.FontSize = 16;
            app.PL18.FontWeight = 'bold';
            app.PL18.FontColor = [0.149 0.149 0.149];
            app.PL18.Position = [935 507 37 26];
            app.PL18.Text = '$';

            % Create S18
            app.S18 = uispinner(app.UIFigure);
            app.S18.Limits = [0 99];
            app.S18.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S18.FontSize = 14;
            app.S18.FontColor = [0.149 0.149 0.149];
            app.S18.Position = [974 507 59 26];

            % Create LanguageDropDownLabel
            app.LanguageDropDownLabel = uilabel(app.UIFigure);
            app.LanguageDropDownLabel.FontSize = 24;
            app.LanguageDropDownLabel.Visible = 'off';
            app.LanguageDropDownLabel.Position = [68 462 125 43];
            app.LanguageDropDownLabel.Text = 'Language';

            % Create O2
            app.O2 = uilabel(app.UIFigure);
            app.O2.FontSize = 16;
            app.O2.FontColor = [0.149 0.149 0.149];
            app.O2.Position = [41 475 132 25];
            app.O2.Text = 'Fried Calamari';

            % Create LanguageDropDown
            app.LanguageDropDown = uidropdown(app.UIFigure);
            app.LanguageDropDown.Items = {'English'};
            app.LanguageDropDown.Visible = 'off';
            app.LanguageDropDown.FontSize = 24;
            app.LanguageDropDown.Position = [208 468 160 32];
            app.LanguageDropDown.Value = 'English';

            % Create P2
            app.P2 = uilabel(app.UIFigure);
            app.P2.FontSize = 16;
            app.P2.FontColor = [0.149 0.149 0.149];
            app.P2.Position = [192 475 42 26];
            app.P2.Text = '7.99';

            % Create PL2
            app.PL2 = uilabel(app.UIFigure);
            app.PL2.HorizontalAlignment = 'center';
            app.PL2.FontSize = 16;
            app.PL2.FontWeight = 'bold';
            app.PL2.FontColor = [0.149 0.149 0.149];
            app.PL2.Position = [235 475 37 26];
            app.PL2.Text = '$';

            % Create S2
            app.S2 = uispinner(app.UIFigure);
            app.S2.Limits = [0 99];
            app.S2.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S2.FontSize = 14;
            app.S2.Position = [274 475 59 26];

            % Create AddPromoCodeorCouponEditFieldLabel
            app.AddPromoCodeorCouponEditFieldLabel = uilabel(app.UIFigure);
            app.AddPromoCodeorCouponEditFieldLabel.HorizontalAlignment = 'center';
            app.AddPromoCodeorCouponEditFieldLabel.FontSize = 18;
            app.AddPromoCodeorCouponEditFieldLabel.Visible = 'off';
            app.AddPromoCodeorCouponEditFieldLabel.Position = [418 463 313 37];
            app.AddPromoCodeorCouponEditFieldLabel.Text = 'Add Promo Code or Coupon';

            % Create O10
            app.O10 = uilabel(app.UIFigure);
            app.O10.FontSize = 16;
            app.O10.FontColor = [0.149 0.149 0.149];
            app.O10.Position = [402 474 132 25];
            app.O10.Text = 'Caprese Salad';

            % Create P10
            app.P10 = uilabel(app.UIFigure);
            app.P10.FontSize = 16;
            app.P10.FontColor = [0.149 0.149 0.149];
            app.P10.Position = [553 474 42 26];
            app.P10.Text = '9.99';

            % Create S10
            app.S10 = uispinner(app.UIFigure);
            app.S10.Limits = [0 99];
            app.S10.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S10.FontSize = 14;
            app.S10.FontColor = [0.149 0.149 0.149];
            app.S10.Position = [635 474 59 26];

            % Create PL10
            app.PL10 = uilabel(app.UIFigure);
            app.PL10.HorizontalAlignment = 'center';
            app.PL10.FontSize = 16;
            app.PL10.FontWeight = 'bold';
            app.PL10.FontColor = [0.149 0.149 0.149];
            app.PL10.Position = [596 474 37 26];
            app.PL10.Text = '$';

            % Create O19
            app.O19 = uilabel(app.UIFigure);
            app.O19.FontSize = 16;
            app.O19.FontColor = [0.149 0.149 0.149];
            app.O19.Position = [741 474 132 25];
            app.O19.Text = 'Iced Tea';

            % Create P19
            app.P19 = uilabel(app.UIFigure);
            app.P19.FontSize = 16;
            app.P19.FontColor = [0.149 0.149 0.149];
            app.P19.Position = [892 474 42 26];
            app.P19.Text = '2.99';

            % Create PL19
            app.PL19 = uilabel(app.UIFigure);
            app.PL19.HorizontalAlignment = 'center';
            app.PL19.FontSize = 16;
            app.PL19.FontWeight = 'bold';
            app.PL19.FontColor = [0.149 0.149 0.149];
            app.PL19.Position = [935 474 37 26];
            app.PL19.Text = '$';

            % Create S19
            app.S19 = uispinner(app.UIFigure);
            app.S19.Limits = [0 99];
            app.S19.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S19.FontSize = 14;
            app.S19.FontColor = [0.149 0.149 0.149];
            app.S19.Position = [974 474 59 26];

            % Create O3
            app.O3 = uilabel(app.UIFigure);
            app.O3.FontSize = 16;
            app.O3.FontColor = [0.149 0.149 0.149];
            app.O3.Position = [41 442 132 25];
            app.O3.Text = 'Bruschetta';

            % Create P3
            app.P3 = uilabel(app.UIFigure);
            app.P3.FontSize = 16;
            app.P3.FontColor = [0.149 0.149 0.149];
            app.P3.Position = [192 442 42 26];
            app.P3.Text = '6.99';

            % Create PL3
            app.PL3 = uilabel(app.UIFigure);
            app.PL3.HorizontalAlignment = 'center';
            app.PL3.FontSize = 16;
            app.PL3.FontWeight = 'bold';
            app.PL3.FontColor = [0.149 0.149 0.149];
            app.PL3.Position = [235 442 37 26];
            app.PL3.Text = '$';

            % Create S3
            app.S3 = uispinner(app.UIFigure);
            app.S3.Limits = [0 99];
            app.S3.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S3.FontSize = 14;
            app.S3.Position = [274 442 59 26];

            % Create O11
            app.O11 = uilabel(app.UIFigure);
            app.O11.FontSize = 16;
            app.O11.FontColor = [0.149 0.149 0.149];
            app.O11.Position = [402 441 132 25];
            app.O11.Text = 'Cobb Salad';

            % Create P11
            app.P11 = uilabel(app.UIFigure);
            app.P11.FontSize = 16;
            app.P11.FontColor = [0.149 0.149 0.149];
            app.P11.Position = [553 441 44 26];
            app.P11.Text = '11.99';

            % Create S11
            app.S11 = uispinner(app.UIFigure);
            app.S11.Limits = [0 99];
            app.S11.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S11.FontSize = 14;
            app.S11.FontColor = [0.149 0.149 0.149];
            app.S11.Position = [635 441 59 26];

            % Create PL11
            app.PL11 = uilabel(app.UIFigure);
            app.PL11.HorizontalAlignment = 'center';
            app.PL11.FontSize = 16;
            app.PL11.FontWeight = 'bold';
            app.PL11.FontColor = [0.149 0.149 0.149];
            app.PL11.Position = [596 441 37 26];
            app.PL11.Text = '$';

            % Create O20
            app.O20 = uilabel(app.UIFigure);
            app.O20.FontSize = 16;
            app.O20.FontColor = [0.149 0.149 0.149];
            app.O20.Position = [741 441 132 25];
            app.O20.Text = 'Lemonade';

            % Create P20
            app.P20 = uilabel(app.UIFigure);
            app.P20.FontSize = 16;
            app.P20.FontColor = [0.149 0.149 0.149];
            app.P20.Position = [892 441 42 26];
            app.P20.Text = '3.49';

            % Create PL20
            app.PL20 = uilabel(app.UIFigure);
            app.PL20.HorizontalAlignment = 'center';
            app.PL20.FontSize = 16;
            app.PL20.FontWeight = 'bold';
            app.PL20.FontColor = [0.149 0.149 0.149];
            app.PL20.Position = [935 441 37 26];
            app.PL20.Text = '$';

            % Create S20
            app.S20 = uispinner(app.UIFigure);
            app.S20.Limits = [0 99];
            app.S20.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S20.FontSize = 14;
            app.S20.FontColor = [0.149 0.149 0.149];
            app.S20.Position = [974 441 59 26];

            % Create CurrencyDropDownLabel
            app.CurrencyDropDownLabel = uilabel(app.UIFigure);
            app.CurrencyDropDownLabel.FontSize = 24;
            app.CurrencyDropDownLabel.Visible = 'off';
            app.CurrencyDropDownLabel.Position = [68 402 125 45];
            app.CurrencyDropDownLabel.Text = 'Currency';

            % Create CurrencyDropDown
            app.CurrencyDropDown = uidropdown(app.UIFigure);
            app.CurrencyDropDown.Items = {'US Dollar', 'LBP'};
            app.CurrencyDropDown.ValueChangedFcn = createCallbackFcn(app, @CurrencyDropDownValueChanged, true);
            app.CurrencyDropDown.Visible = 'off';
            app.CurrencyDropDown.FontSize = 24;
            app.CurrencyDropDown.Position = [208 408 160 32];
            app.CurrencyDropDown.Value = 'US Dollar';

            % Create PromoCodeField
            app.PromoCodeField = uieditfield(app.UIFigure, 'text');
            app.PromoCodeField.HorizontalAlignment = 'center';
            app.PromoCodeField.FontSize = 18;
            app.PromoCodeField.Visible = 'off';
            app.PromoCodeField.Position = [418 412 203 27];

            % Create O12
            app.O12 = uilabel(app.UIFigure);
            app.O12.FontSize = 16;
            app.O12.FontColor = [0.149 0.149 0.149];
            app.O12.Position = [402 409 132 25];
            app.O12.Text = 'Spinach Salad';

            % Create P12
            app.P12 = uilabel(app.UIFigure);
            app.P12.FontSize = 16;
            app.P12.FontColor = [0.149 0.149 0.149];
            app.P12.Position = [553 409 45 26];
            app.P12.Text = '12.99';

            % Create PromoCodeSubmit
            app.PromoCodeSubmit = uibutton(app.UIFigure, 'push');
            app.PromoCodeSubmit.ButtonPushedFcn = createCallbackFcn(app, @PromoCodeSubmitPushed, true);
            app.PromoCodeSubmit.FontSize = 16;
            app.PromoCodeSubmit.Visible = 'off';
            app.PromoCodeSubmit.Position = [631 412 100 28];
            app.PromoCodeSubmit.Text = 'Submit';

            % Create S12
            app.S12 = uispinner(app.UIFigure);
            app.S12.Limits = [0 99];
            app.S12.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S12.FontSize = 14;
            app.S12.FontColor = [0.149 0.149 0.149];
            app.S12.Position = [635 409 59 26];

            % Create PL12
            app.PL12 = uilabel(app.UIFigure);
            app.PL12.HorizontalAlignment = 'center';
            app.PL12.FontSize = 16;
            app.PL12.FontWeight = 'bold';
            app.PL12.FontColor = [0.149 0.149 0.149];
            app.PL12.Position = [596 409 37 26];
            app.PL12.Text = '$';

            % Create O21
            app.O21 = uilabel(app.UIFigure);
            app.O21.FontSize = 16;
            app.O21.FontColor = [0.149 0.149 0.149];
            app.O21.Position = [741 409 132 25];
            app.O21.Text = 'Local Beer';

            % Create P21
            app.P21 = uilabel(app.UIFigure);
            app.P21.FontSize = 16;
            app.P21.FontColor = [0.149 0.149 0.149];
            app.P21.Position = [892 409 42 26];
            app.P21.Text = '4.99';

            % Create PL21
            app.PL21 = uilabel(app.UIFigure);
            app.PL21.HorizontalAlignment = 'center';
            app.PL21.FontSize = 16;
            app.PL21.FontWeight = 'bold';
            app.PL21.FontColor = [0.149 0.149 0.149];
            app.PL21.Position = [935 409 37 26];
            app.PL21.Text = '$';

            % Create S21
            app.S21 = uispinner(app.UIFigure);
            app.S21.Limits = [0 99];
            app.S21.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S21.FontSize = 14;
            app.S21.FontColor = [0.149 0.149 0.149];
            app.S21.Position = [974 409 59 26];

            % Create SoupDropDown_3Label
            app.SoupDropDown_3Label = uilabel(app.UIFigure);
            app.SoupDropDown_3Label.HorizontalAlignment = 'center';
            app.SoupDropDown_3Label.FontSize = 16;
            app.SoupDropDown_3Label.FontColor = [0.149 0.149 0.149];
            app.SoupDropDown_3Label.Position = [43 399 42 22];
            app.SoupDropDown_3Label.Text = 'Soup';

            % Create SoupDropDown
            app.SoupDropDown = uidropdown(app.UIFigure);
            app.SoupDropDown.Items = {'< None >', 'Asparagus (10$)', 'Chinese Noodle (7$)', 'Egg Drop (8$)', 'Fish and Tofu  (11$)', 'Hototay (6$)'};
            app.SoupDropDown.ItemsData = [0 10 7 8 11 6];
            app.SoupDropDown.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.SoupDropDown.FontSize = 16;
            app.SoupDropDown.FontColor = [0.149 0.149 0.149];
            app.SoupDropDown.Position = [114 399 219 22];
            app.SoupDropDown.Value = 0;

            % Create PromoCodeNote
            app.PromoCodeNote = uilabel(app.UIFigure);
            app.PromoCodeNote.HorizontalAlignment = 'center';
            app.PromoCodeNote.FontAngle = 'italic';
            app.PromoCodeNote.Visible = 'off';
            app.PromoCodeNote.Position = [418 388 313 22];
            app.PromoCodeNote.Text = '';

            % Create SandwichesLabel
            app.SandwichesLabel = uilabel(app.UIFigure);
            app.SandwichesLabel.HorizontalAlignment = 'center';
            app.SandwichesLabel.FontName = 'Segoe UI';
            app.SandwichesLabel.FontSize = 20;
            app.SandwichesLabel.FontWeight = 'bold';
            app.SandwichesLabel.FontColor = [0.149 0.149 0.149];
            app.SandwichesLabel.Position = [1 351 350 40];
            app.SandwichesLabel.Text = 'Sandwiches';

            % Create SeafoodLabel
            app.SeafoodLabel = uilabel(app.UIFigure);
            app.SeafoodLabel.HorizontalAlignment = 'center';
            app.SeafoodLabel.FontName = 'Segoe UI';
            app.SeafoodLabel.FontSize = 20;
            app.SeafoodLabel.FontWeight = 'bold';
            app.SeafoodLabel.FontColor = [0.149 0.149 0.149];
            app.SeafoodLabel.Position = [351 351 350 40];
            app.SeafoodLabel.Text = 'Seafood';

            % Create CalculationsLabel
            app.CalculationsLabel = uilabel(app.UIFigure);
            app.CalculationsLabel.HorizontalAlignment = 'center';
            app.CalculationsLabel.FontName = 'Segoe UI';
            app.CalculationsLabel.FontSize = 20;
            app.CalculationsLabel.FontWeight = 'bold';
            app.CalculationsLabel.FontColor = [0.149 0.149 0.149];
            app.CalculationsLabel.Position = [701 351 350 40];
            app.CalculationsLabel.Text = 'Calculations';

            % Create AddressLabel
            app.AddressLabel = uilabel(app.UIFigure);
            app.AddressLabel.FontSize = 18;
            app.AddressLabel.Visible = 'off';
            app.AddressLabel.Position = [68 290 663 44];
            app.AddressLabel.Text = {'Address Line:              Highway 375, Rachel, NV 89001, United States'; 'Customer Support:     +1 (775) 729-2515'};

            % Create O4
            app.O4 = uilabel(app.UIFigure);
            app.O4.FontSize = 16;
            app.O4.FontColor = [0.149 0.149 0.149];
            app.O4.Position = [41 306 132 25];
            app.O4.Text = 'Classic BLT';

            % Create P4
            app.P4 = uilabel(app.UIFigure);
            app.P4.FontSize = 16;
            app.P4.FontColor = [0.149 0.149 0.149];
            app.P4.Position = [192 306 42 26];
            app.P4.Text = '8.99';

            % Create PL4
            app.PL4 = uilabel(app.UIFigure);
            app.PL4.HorizontalAlignment = 'center';
            app.PL4.FontSize = 16;
            app.PL4.FontWeight = 'bold';
            app.PL4.FontColor = [0.149 0.149 0.149];
            app.PL4.Position = [235 306 37 26];
            app.PL4.Text = '$';

            % Create S4
            app.S4 = uispinner(app.UIFigure);
            app.S4.Limits = [0 99];
            app.S4.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S4.FontSize = 14;
            app.S4.FontColor = [0.149 0.149 0.149];
            app.S4.Position = [274 306 59 26];

            % Create O13
            app.O13 = uilabel(app.UIFigure);
            app.O13.FontSize = 16;
            app.O13.FontColor = [0.149 0.149 0.149];
            app.O13.Position = [402 306 132 25];
            app.O13.Text = 'Grilled Salmon';

            % Create P13
            app.P13 = uilabel(app.UIFigure);
            app.P13.FontSize = 16;
            app.P13.FontColor = [0.149 0.149 0.149];
            app.P13.Position = [553 306 45 26];
            app.P13.Text = '18.99';

            % Create S13
            app.S13 = uispinner(app.UIFigure);
            app.S13.Limits = [0 99];
            app.S13.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S13.FontSize = 14;
            app.S13.FontColor = [0.149 0.149 0.149];
            app.S13.Position = [635 306 59 26];

            % Create PL13
            app.PL13 = uilabel(app.UIFigure);
            app.PL13.HorizontalAlignment = 'center';
            app.PL13.FontSize = 16;
            app.PL13.FontWeight = 'bold';
            app.PL13.FontColor = [0.149 0.149 0.149];
            app.PL13.Position = [596 306 37 26];
            app.PL13.Text = '$';

            % Create CalcNote
            app.CalcNote = uilabel(app.UIFigure);
            app.CalcNote.HorizontalAlignment = 'center';
            app.CalcNote.FontSize = 14;
            app.CalcNote.FontAngle = 'italic';
            app.CalcNote.FontColor = [0.149 0.149 0.149];
            app.CalcNote.Position = [701 321 349 31];
            app.CalcNote.Text = 'State and local tax rates apply to all purchases.';

            % Create O5
            app.O5 = uilabel(app.UIFigure);
            app.O5.FontSize = 16;
            app.O5.FontColor = [0.149 0.149 0.149];
            app.O5.Position = [41 273 141 25];
            app.O5.Text = 'Turkey Club';

            % Create P5
            app.P5 = uilabel(app.UIFigure);
            app.P5.FontSize = 16;
            app.P5.FontColor = [0.149 0.149 0.149];
            app.P5.Position = [192 273 45 26];
            app.P5.Text = '8.99';

            % Create PL5
            app.PL5 = uilabel(app.UIFigure);
            app.PL5.HorizontalAlignment = 'center';
            app.PL5.FontSize = 16;
            app.PL5.FontWeight = 'bold';
            app.PL5.FontColor = [0.149 0.149 0.149];
            app.PL5.Position = [235 273 37 26];
            app.PL5.Text = '$';

            % Create S5
            app.S5 = uispinner(app.UIFigure);
            app.S5.Limits = [0 99];
            app.S5.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S5.FontSize = 14;
            app.S5.FontColor = [0.149 0.149 0.149];
            app.S5.Position = [274 273 59 26];

            % Create O14
            app.O14 = uilabel(app.UIFigure);
            app.O14.FontSize = 16;
            app.O14.FontColor = [0.149 0.149 0.149];
            app.O14.Position = [402 273 147 25];
            app.O14.Text = 'Clam Chowder';

            % Create P14
            app.P14 = uilabel(app.UIFigure);
            app.P14.FontSize = 16;
            app.P14.FontColor = [0.149 0.149 0.149];
            app.P14.Position = [553 273 45 26];
            app.P14.Text = '15.99';

            % Create S14
            app.S14 = uispinner(app.UIFigure);
            app.S14.Limits = [0 99];
            app.S14.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S14.FontSize = 14;
            app.S14.FontColor = [0.149 0.149 0.149];
            app.S14.Position = [635 273 59 26];

            % Create PL14
            app.PL14 = uilabel(app.UIFigure);
            app.PL14.HorizontalAlignment = 'center';
            app.PL14.FontSize = 16;
            app.PL14.FontWeight = 'bold';
            app.PL14.FontColor = [0.149 0.149 0.149];
            app.PL14.Position = [596 273 37 26];
            app.PL14.Text = '$';

            % Create QRCaption
            app.QRCaption = uilabel(app.UIFigure);
            app.QRCaption.HorizontalAlignment = 'center';
            app.QRCaption.FontAngle = 'italic';
            app.QRCaption.Visible = 'off';
            app.QRCaption.Position = [784 289 228 22];
            app.QRCaption.Text = '***Google Maps Link to Location';

            % Create CopyrightNote
            app.CopyrightNote = uilabel(app.UIFigure);
            app.CopyrightNote.HorizontalAlignment = 'center';
            app.CopyrightNote.FontSize = 16;
            app.CopyrightNote.FontAngle = 'italic';
            app.CopyrightNote.Visible = 'off';
            app.CopyrightNote.Position = [2 184 1049 73];
            app.CopyrightNote.Text = {'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS WHERE ANY EXPRESS OR IMPLIED WARRANTIES, '; 'INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A'; 'PARTICULAR PURPOSE ARE DISCLAIMED.'};

            % Create O6
            app.O6 = uilabel(app.UIFigure);
            app.O6.FontSize = 16;
            app.O6.FontColor = [0.149 0.149 0.149];
            app.O6.Position = [41 240 132 25];
            app.O6.Text = 'Veggie Delight';

            % Create P6
            app.P6 = uilabel(app.UIFigure);
            app.P6.FontSize = 16;
            app.P6.FontColor = [0.149 0.149 0.149];
            app.P6.Position = [192 240 42 26];
            app.P6.Text = '7.99';

            % Create PL6
            app.PL6 = uilabel(app.UIFigure);
            app.PL6.HorizontalAlignment = 'center';
            app.PL6.FontSize = 16;
            app.PL6.FontWeight = 'bold';
            app.PL6.FontColor = [0.149 0.149 0.149];
            app.PL6.Position = [235 240 37 26];
            app.PL6.Text = '$';

            % Create S6
            app.S6 = uispinner(app.UIFigure);
            app.S6.Limits = [0 99];
            app.S6.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S6.FontSize = 14;
            app.S6.FontColor = [0.149 0.149 0.149];
            app.S6.Position = [274 240 59 26];

            % Create O15
            app.O15 = uilabel(app.UIFigure);
            app.O15.FontSize = 16;
            app.O15.FontColor = [0.149 0.149 0.149];
            app.O15.Position = [402 240 132 25];
            app.O15.Text = 'Lobster Bisque';

            % Create P15
            app.P15 = uilabel(app.UIFigure);
            app.P15.FontSize = 16;
            app.P15.FontColor = [0.149 0.149 0.149];
            app.P15.Position = [553 240 45 26];
            app.P15.Text = '12.99';

            % Create S15
            app.S15 = uispinner(app.UIFigure);
            app.S15.Limits = [0 99];
            app.S15.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S15.FontSize = 14;
            app.S15.FontColor = [0.149 0.149 0.149];
            app.S15.Position = [635 240 59 26];

            % Create PL15
            app.PL15 = uilabel(app.UIFigure);
            app.PL15.HorizontalAlignment = 'center';
            app.PL15.FontSize = 16;
            app.PL15.FontWeight = 'bold';
            app.PL15.FontColor = [0.149 0.149 0.149];
            app.PL15.Position = [596 240 37 26];
            app.PL15.Text = '$';

            % Create TipsSliderLabel
            app.TipsSliderLabel = uilabel(app.UIFigure);
            app.TipsSliderLabel.HorizontalAlignment = 'right';
            app.TipsSliderLabel.FontSize = 18;
            app.TipsSliderLabel.FontColor = [0.149 0.149 0.149];
            app.TipsSliderLabel.Position = [734 261 71 23];
            app.TipsSliderLabel.Text = 'Tips (%)';

            % Create TipsSlider
            app.TipsSlider = uislider(app.UIFigure);
            app.TipsSlider.Limits = [0 20];
            app.TipsSlider.MajorTicks = [0 5 10 15 20];
            app.TipsSlider.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.TipsSlider.ValueChangingFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.TipsSlider.MinorTicks = [0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20];
            app.TipsSlider.FontSize = 18;
            app.TipsSlider.FontColor = [0.149 0.149 0.149];
            app.TipsSlider.Position = [826 271 183 3];

            % Create O7
            app.O7 = uilabel(app.UIFigure);
            app.O7.FontSize = 16;
            app.O7.FontColor = [0.149 0.149 0.149];
            app.O7.Position = [41 207 132 25];
            app.O7.Text = 'Italian Sub';

            % Create P7
            app.P7 = uilabel(app.UIFigure);
            app.P7.FontSize = 16;
            app.P7.FontColor = [0.149 0.149 0.149];
            app.P7.Position = [192 208 45 26];
            app.P7.Text = '10.99';

            % Create PL7
            app.PL7 = uilabel(app.UIFigure);
            app.PL7.HorizontalAlignment = 'center';
            app.PL7.FontSize = 16;
            app.PL7.FontWeight = 'bold';
            app.PL7.FontColor = [0.149 0.149 0.149];
            app.PL7.Position = [235 208 37 26];
            app.PL7.Text = '$';

            % Create S7
            app.S7 = uispinner(app.UIFigure);
            app.S7.Limits = [0 99];
            app.S7.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S7.FontSize = 14;
            app.S7.FontColor = [0.149 0.149 0.149];
            app.S7.Position = [274 208 59 26];

            % Create O16
            app.O16 = uilabel(app.UIFigure);
            app.O16.FontSize = 16;
            app.O16.FontColor = [0.149 0.149 0.149];
            app.O16.Position = [402 208 132 25];
            app.O16.Text = 'Shrimp Scampi';

            % Create P16
            app.P16 = uilabel(app.UIFigure);
            app.P16.FontSize = 16;
            app.P16.FontColor = [0.149 0.149 0.149];
            app.P16.Position = [553 208 45 26];
            app.P16.Text = '20.99';

            % Create S16
            app.S16 = uispinner(app.UIFigure);
            app.S16.Limits = [0 99];
            app.S16.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S16.FontSize = 14;
            app.S16.FontColor = [0.149 0.149 0.149];
            app.S16.Position = [635 208 59 26];

            % Create PL16
            app.PL16 = uilabel(app.UIFigure);
            app.PL16.HorizontalAlignment = 'center';
            app.PL16.FontSize = 16;
            app.PL16.FontWeight = 'bold';
            app.PL16.FontColor = [0.149 0.149 0.149];
            app.PL16.Position = [596 208 37 26];
            app.PL16.Text = '$';

            % Create O8
            app.O8 = uilabel(app.UIFigure);
            app.O8.FontSize = 16;
            app.O8.FontColor = [0.149 0.149 0.149];
            app.O8.Position = [41 172 132 25];
            app.O8.Text = 'Reuben';

            % Create P8
            app.P8 = uilabel(app.UIFigure);
            app.P8.FontSize = 16;
            app.P8.FontColor = [0.149 0.149 0.149];
            app.P8.Position = [192 172 42 26];
            app.P8.Text = '9.99';

            % Create PL8
            app.PL8 = uilabel(app.UIFigure);
            app.PL8.HorizontalAlignment = 'center';
            app.PL8.FontSize = 16;
            app.PL8.FontWeight = 'bold';
            app.PL8.FontColor = [0.149 0.149 0.149];
            app.PL8.Position = [235 172 37 26];
            app.PL8.Text = '$';

            % Create S8
            app.S8 = uispinner(app.UIFigure);
            app.S8.Limits = [0 99];
            app.S8.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S8.FontSize = 14;
            app.S8.FontColor = [0.149 0.149 0.149];
            app.S8.Position = [274 172 59 26];

            % Create Copyright
            app.Copyright = uilabel(app.UIFigure);
            app.Copyright.HorizontalAlignment = 'center';
            app.Copyright.FontSize = 18;
            app.Copyright.Visible = 'off';
            app.Copyright.Position = [355 80 343 120];
            app.Copyright.Text = {'Copyright (c) 2023'; ' Kris Antony Atallah & Anthony Gemayel '; 'All rights reserved.'; ''};

            % Create O17
            app.O17 = uilabel(app.UIFigure);
            app.O17.FontSize = 16;
            app.O17.FontColor = [0.149 0.149 0.149];
            app.O17.Position = [402 172 132 25];
            app.O17.Text = 'Steamed Mussels';

            % Create P17
            app.P17 = uilabel(app.UIFigure);
            app.P17.FontSize = 16;
            app.P17.FontColor = [0.149 0.149 0.149];
            app.P17.Position = [553 172 45 26];
            app.P17.Text = '17.99';

            % Create S17
            app.S17 = uispinner(app.UIFigure);
            app.S17.Limits = [0 99];
            app.S17.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.S17.FontSize = 14;
            app.S17.FontColor = [0.149 0.149 0.149];
            app.S17.Position = [635 172 59 26];

            % Create PL17
            app.PL17 = uilabel(app.UIFigure);
            app.PL17.HorizontalAlignment = 'center';
            app.PL17.FontSize = 16;
            app.PL17.FontWeight = 'bold';
            app.PL17.FontColor = [0.149 0.149 0.149];
            app.PL17.Position = [596 172 37 26];
            app.PL17.Text = '$';

            % Create SubtotalLabel
            app.SubtotalLabel = uilabel(app.UIFigure);
            app.SubtotalLabel.FontSize = 18;
            app.SubtotalLabel.FontWeight = 'bold';
            app.SubtotalLabel.FontColor = [0.149 0.149 0.149];
            app.SubtotalLabel.Position = [741 174 161 30];
            app.SubtotalLabel.Text = 'Subtotal';

            % Create SubtotalField
            app.SubtotalField = uieditfield(app.UIFigure, 'numeric');
            app.SubtotalField.Limits = [0 Inf];
            app.SubtotalField.ValueDisplayFormat = '%11.4g $';
            app.SubtotalField.Editable = 'off';
            app.SubtotalField.HorizontalAlignment = 'center';
            app.SubtotalField.FontSize = 18;
            app.SubtotalField.FontWeight = 'bold';
            app.SubtotalField.FontColor = [0.149 0.149 0.149];
            app.SubtotalField.Position = [892 173 141 29];

            % Create DishoftheDayDropDownLabel
            app.DishoftheDayDropDownLabel = uilabel(app.UIFigure);
            app.DishoftheDayDropDownLabel.HorizontalAlignment = 'center';
            app.DishoftheDayDropDownLabel.FontSize = 20;
            app.DishoftheDayDropDownLabel.FontWeight = 'bold';
            app.DishoftheDayDropDownLabel.FontColor = [0.149 0.149 0.149];
            app.DishoftheDayDropDownLabel.Position = [41 112 196 30];
            app.DishoftheDayDropDownLabel.Text = 'Dish of the Day';

            % Create DishoftheDayDropDown
            app.DishoftheDayDropDown = uidropdown(app.UIFigure);
            app.DishoftheDayDropDown.Items = {'< Select Date >'};
            app.DishoftheDayDropDown.ItemsData = {'0', '0', '0'};
            app.DishoftheDayDropDown.ValueChangedFcn = createCallbackFcn(app, @S1ValueChanged, true);
            app.DishoftheDayDropDown.FontSize = 20;
            app.DishoftheDayDropDown.FontColor = [0.149 0.149 0.149];
            app.DishoftheDayDropDown.Position = [237 111 456 27];
            app.DishoftheDayDropDown.Value = '0';

            % Create SubtotalwTaxLabel
            app.SubtotalwTaxLabel = uilabel(app.UIFigure);
            app.SubtotalwTaxLabel.FontSize = 18;
            app.SubtotalwTaxLabel.FontWeight = 'bold';
            app.SubtotalwTaxLabel.FontColor = [0.149 0.149 0.149];
            app.SubtotalwTaxLabel.Position = [741 127 161 30];
            app.SubtotalwTaxLabel.Text = 'Subtotal + TAX';

            % Create SubtotalwTaxField
            app.SubtotalwTaxField = uieditfield(app.UIFigure, 'numeric');
            app.SubtotalwTaxField.Limits = [0 Inf];
            app.SubtotalwTaxField.ValueDisplayFormat = '%11.4g $';
            app.SubtotalwTaxField.Editable = 'off';
            app.SubtotalwTaxField.HorizontalAlignment = 'center';
            app.SubtotalwTaxField.FontSize = 18;
            app.SubtotalwTaxField.FontWeight = 'bold';
            app.SubtotalwTaxField.FontColor = [0.149 0.149 0.149];
            app.SubtotalwTaxField.Position = [892 127 141 29];

            % Create SettingsButton
            app.SettingsButton = uibutton(app.UIFigure, 'push');
            app.SettingsButton.ButtonPushedFcn = createCallbackFcn(app, @SettingsButtonPushed, true);
            app.SettingsButton.FontName = 'Segoe UI';
            app.SettingsButton.FontSize = 24;
            app.SettingsButton.FontWeight = 'bold';
            app.SettingsButton.FontColor = [0.149 0.149 0.149];
            app.SettingsButton.Position = [41 29 151 52];
            app.SettingsButton.Text = 'Settings';

            % Create LightLabel
            app.LightLabel = uilabel(app.UIFigure);
            app.LightLabel.HorizontalAlignment = 'center';
            app.LightLabel.FontName = 'Segoe UI';
            app.LightLabel.FontSize = 18;
            app.LightLabel.FontWeight = 'bold';
            app.LightLabel.FontColor = [0.149 0.149 0.149];
            app.LightLabel.Position = [402 39 50 32];
            app.LightLabel.Text = 'Light';

            % Create Switch
            app.Switch = uiswitch(app.UIFigure, 'slider');
            app.Switch.Items = {'L', 'D'};
            app.Switch.ValueChangedFcn = createCallbackFcn(app, @SwitchValueChanged, true);
            app.Switch.FontSize = 0.1;
            app.Switch.Position = [487 33 86 38];
            app.Switch.Value = 'L';

            % Create DarkLabel
            app.DarkLabel = uilabel(app.UIFigure);
            app.DarkLabel.HorizontalAlignment = 'center';
            app.DarkLabel.FontName = 'Segoe UI';
            app.DarkLabel.FontSize = 18;
            app.DarkLabel.FontWeight = 'bold';
            app.DarkLabel.FontColor = [0.149 0.149 0.149];
            app.DarkLabel.Position = [604 39 50 33];
            app.DarkLabel.Text = 'Dark';

            % Create ExitButton
            app.ExitButton = uibutton(app.UIFigure, 'push');
            app.ExitButton.ButtonPushedFcn = createCallbackFcn(app, @ExitButtonPushed, true);
            app.ExitButton.FontName = 'Segoe UI';
            app.ExitButton.FontSize = 24;
            app.ExitButton.FontWeight = 'bold';
            app.ExitButton.FontColor = [0.149 0.149 0.149];
            app.ExitButton.Position = [861 29 151 52];
            app.ExitButton.Text = 'Exit';

            % Show the figure after all components are created
            app.UIFigure.Visible = 'on';
        end
    end

    % App creation and deletion
    methods (Access = public)

        % Construct app
        function app = Matlab_Project

            % Create UIFigure and components
            createComponents(app)

            % Register the app with App Designer
            registerApp(app, app.UIFigure)

            if nargout == 0
                clear app
            end
        end

        % Code that executes before app deletion
        function delete(app)

            % Delete UIFigure when app is deleted
            delete(app.UIFigure)
        end
    end
end