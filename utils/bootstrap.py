class BootStrapForm:
    exclude_field_list = []

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        #{'title':对象,'percent’:对象}
        for name,field in self.fields.items():
            if name in self.exclude_field_list:
                continue
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{}'.format(field.label)