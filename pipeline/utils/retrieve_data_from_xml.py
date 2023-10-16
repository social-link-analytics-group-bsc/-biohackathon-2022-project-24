from lxml import etree


class XmlParser:
    def __init__(self, xml_document):
        if isinstance(xml_document, str):
            # Parse the XML string into an Element object
            self.xml_document = etree.fromstring(xml_document)
        else:
            # If it's already an Element object, use it directly
            self.xml_document = xml_document


    def abstract(self):
        # Define the XPath expression to find abstract text with sections
        xpath_expression_with_sec = ".//abstract/sec"

        # Try to find the abstract element with sections
        abstract_elements = self.xml_document.findall(xpath_expression_with_sec)

        abstract_elements = [el.text for el in abstract_elements if el.text is not None]
        if abstract_elements:
            # If abstracts with sections are found, concatenate their text
            abstract_text = " ".join(abstract_element.strip() for abstract_element in abstract_elements)
            return abstract_text

        # If no abstracts with sections are found, try to find abstracts without sections
        xpath_expression_no_sec = ".//abstract"
        abstract_elements = self.xml_document.findall(xpath_expression_no_sec)

        abstract_elements = [el.text for el in abstract_elements if el.text is not None]
        if abstract_elements:
            # If abstracts without sections are found, concatenate their text
            abstract_text = " ".join(abstract_element.strip() for abstract_element in abstract_elements)
            return abstract_text
        
        # If no abstracts with sections are found, try to find abstracts without sections
        xpath_expression_no_sec = ".//abstract/p"
        abstract_elements = self.xml_document.findall(xpath_expression_no_sec)

        abstract_elements = [el.text for el in abstract_elements if el.text is not None]
        if abstract_elements:
            # If abstracts without sections are found, concatenate their text
            abstract_text = " ".join(abstract_element.strip() for abstract_element in abstract_elements)
            return abstract_text

    def article_type(self):
        article_type = self.xml_document.get(".//@article-type")
        return article_type

    def article_title(self):
        title_xpath = ".//article-title"
        title_element = self.xml_document.find(title_xpath)
        title = title_element.text if title_element is not None else None
        return title

    def journal_title(self):
        journal_title_xpath = ".//journal-title"
        journal_title_element = self.xml_document.find(journal_title_xpath)
        journal_title = (
            journal_title_element.text if journal_title_element is not None else None
        )
        return journal_title

    def publication_date(self):
        # FIXME change that one to match the publication date not the other one

        pub_date_xpath = ".//pub-date"
        pub_date_element = self.xml_document.find(pub_date_xpath)
        if pub_date_element is not None:
            year = pub_date_element.findtext("year")
            month = pub_date_element.findtext("month")
            day = pub_date_element.findtext("day")
            return {"year": year, "month": month, "day": day}
        return None

    def article_categories(self):
        categories_xpath = ".//article-categories/subj-group/subject"
        categories_elements = self.xml_document.findall(categories_xpath)
        if categories_elements is not None:
            categories = [el.text for el in categories_elements]
        return categories

    def copyright_info(self):
        copyright_xpath = ".//permissions/copyright-statement"
        copyright_element = self.xml_document.find(copyright_xpath)
        copyright_ = copyright_element.text if copyright_element is not None else None
        return copyright_

    def keywords(self):
        kwd_xpath = ".//kwd-group/kwd"
        kwd_elements = self.xml_document.findall(kwd_xpath)
        if kwd_elements is not None:
            return [el.text for el in kwd_elements]

    def authors(self):
        author_xpath = ".//contrib[@contrib-type='author']"
        author_elements = self.xml_document.findall(author_xpath)
        authors = []
        for author_element in author_elements:
            name_element = author_element.find("name")
            if name_element is not None:
                surname = name_element.findtext("surname")
                given_names = name_element.findtext("given-names")
                authors.append(f"{given_names} {surname}")
        return authors

    def ids(self):
        dict_ids = dict()
        pmcid_xpath = ".//article-id[@pub-id-type='pmcid']"
        publisher_id_xpath = ".//article-id[@pub-id-type='publisher-id']"
        doi_xpath = ".//article-id[@pub-id-type='doi']"
        pmcid_element = self.xml_document.find(pmcid_xpath)
        publisher_id_element = self.xml_document.find(publisher_id_xpath)
        doi_element = self.xml_document.find(doi_xpath)
        dict_ids["pmcid"] = pmcid_element.text if pmcid_element is not None else None
        dict_ids["publisher_id"] = (
            publisher_id_element.text if publisher_id_element is not None else None
        )
        dict_ids["doi"] = doi_element.text if doi_element is not None else None
        return dict_ids

    def funding(self):
        funding_xpath = ".//funding-source"
        funding_elements = self.xml_document.findall(funding_xpath)
        funding_info = []

        for funding_element in funding_elements:
            funding_dict = {}
            try:
                funding_dict['institution'] = funding_element.find(".//institution").text
            except AttributeError:
                pass
            try:
                funding_dict['award_id'] = funding_element.find(".//award-id").text
            except AttributeError:
                pass
            try:
                funding_dict['recipient_name'] = funding_element.find(
                ".//principal-award-recipient/name"
            ).text
            except AttributeError:
                pass
            if funding_dict:
                funding_info.append(funding_dict)
        return funding_info


    def sections(self):
        # FIXME: Just apply the way it was in the Sergi code
        # But I suspect it is not the only way and there is something in EuropePMC
        # About different type of field possible to retrieve.
        # In any case will do like that
        section_fields = ["intro", "methods", "results", "discussion"]
        dict_section = {k: None for k in section_fields}

        sections_xpath = ".//body/sec"
        sec_elements = self.xml_document.findall(sections_xpath)
        # Iterate through the sec elements
        for sec in sec_elements:
            sec_type = sec.attrib.get("sec-type", "").lower()
            # Check if the sec-type attribute matches any of the section fields
            for section in section_fields:
                if section in sec_type:
                    # Extract the text content of the section (text without tags)
                    section_text = "".join(sec.itertext())
                    dict_section[section] = section_text.replace('"', "'")
        for k in dict_section:
            if dict_section[k] is not None:
                return dict_section


class DynamicXmlParser(XmlParser):
    def __init__(self, xml_document):
        super().__init__(xml_document)
        self.data = {}  # Initialize a dictionary to store method results
        self.data_status = {}  # Initialize a dict to store the method status

        # Get all the methods from the parent class
        parent_class_methods = [
            func
            for func in dir(self)
            if callable(getattr(self, func)) and not func.startswith("__")
        ]

        # Call each method and store the result in the data dictionary
        for method_name in parent_class_methods:
            method = getattr(self, method_name)
            result = method()
            self.data[method_name] = result

    def check_methods(self):
        # Check which methods returned False and create a dynamic dictionary
        for method_name in self.data:
            if self.data[method_name]:
                self.data_status[method_name] = True
            else:
                self.data_status[method_name] = False

